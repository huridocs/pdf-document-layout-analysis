from adapters.infrastructure.markup_conversion.OutputFormat import OutputFormat
from adapters.infrastructure.translation.decode_html_content import decode_html
from adapters.infrastructure.translation.decode_markdown_content import decode_markdown
from adapters.infrastructure.translation.encode_html_content import encode_html
from adapters.infrastructure.translation.encode_markdown_content import encode_markdown
from domain.SegmentBox import SegmentBox
from pdf_token_type_labels.TokenType import TokenType
from ollama import Client

prompt = """Please translate the following text into {target_language}. Follow these guidelines:
1. Maintain the original layout and formatting.
2. Translate all text accurately without omitting any part of the content.
3. Preserve the tone and style of the original text.
4. Do not include any additional comments, notes, or explanations in the output; provide only the translated text.
5. Do not change, remove, or add any markdown symbols (such as *, _, #, [ ], ( ), -, or backticks). Only translate the visible text.
6. Do not translate URLs, email addresses, or code snippets. Only translate the human-readable text.
7. If you see custom tags (such as [DOC_REF], [IT], [B], [LINK]), **translate the text inside the tags, but do not change, remove, or translate the tags themselves.** The tags must appear in the same positions in the output as in the input.
8. The output must have the same number of lines as the input. Do not reorder any lines or sentences.

**Only translate the text between ``` and ```. Do not output any other text or character. Do not include the ``` characters in the output.**

Here is the text to be translated:

```
{text_to_translate}
```
"""


def get_translation(model: str, content: str) -> str:
    response = Client(host="http://localhost:11434").chat(model=model, messages=[{"role": "user", "content": content}])
    return response["message"]["content"].replace("```", "").strip()


def get_table_of_contents(vgt_segments: list[SegmentBox]) -> str:
    title_segments = [s for s in vgt_segments if s.type in {TokenType.TITLE, TokenType.SECTION_HEADER}]
    table_of_contents = "# Table of Contents\n\n"
    for segment in title_segments:
        if not segment.text.strip():
            continue
        first_word = segment.text.split()[0]
        indentation = max(0, first_word.count(".") - 1)
        content = "  " * indentation + "- [" + segment.text + "](#" + segment.id + ")\n"
        table_of_contents += content
    table_of_contents += "\n"
    return table_of_contents + "\n\n"


def translate_markdown(
    segments: list[SegmentBox],
    markdown_parts: list[str],
    model: str,
    target_language: str,
    extract_toc: bool = False,
) -> str:
    translated_markdown_parts: list[str] = []
    title_segments = []
    if extract_toc:
        markdown_parts = markdown_parts[1:]
    for index, markdown_part in enumerate(markdown_parts):
        markdown_part = markdown_part.strip()
        if not markdown_part:
            continue
        if segments[index].type == TokenType.PICTURE:
            translated_markdown_parts.append(markdown_part)
            continue
        if segments[index].type == TokenType.TABLE:
            anchor, table_html = markdown_part.split("\n", 1)
            content = prompt.format(target_language=target_language, text_to_translate=table_html)
            response = get_translation(model, content)
            translated_markdown_parts.append(anchor + "\n" + response)
            continue
        if segments[index].type in {TokenType.TITLE, TokenType.SECTION_HEADER}:
            anchor, text = markdown_part.split("\n")
            content = prompt.format(target_language=target_language, text_to_translate=text)
            response = get_translation(model, content)
            translated_markdown_parts.append(anchor + "\n" + response)
            if extract_toc:
                title_segments.append(segments[index])
                title_segments[-1].text = response.replace("#", "").strip()
            continue
        if segments[index].type == TokenType.FORMULA:
            translated_markdown_parts.append(markdown_part)
            continue
        encoded_text, link_map, doc_ref_map = encode_markdown(markdown_part)
        content = prompt.format(target_language=target_language, text_to_translate=encoded_text)
        response = get_translation(model, content)
        translated_markdown_parts.append(decode_markdown(response, link_map, doc_ref_map))
    if extract_toc:
        translated_markdown_parts.insert(0, get_table_of_contents(title_segments))
    return "\n\n".join(translated_markdown_parts)


def translate_html(
    segments: list[SegmentBox],
    html_parts: list[str],
    model: str,
    target_language: str,
    extract_toc: bool = False,
) -> str:
    translated_html_parts: list[str] = []
    title_segments = []
    if extract_toc:
        html_parts = html_parts[1:]
    for index, html_part in enumerate(html_parts):
        html_part = html_part.strip()
        if not html_part:
            continue
        if segments[index].type == TokenType.PICTURE:
            translated_html_parts.append(html_part)
            continue
        if segments[index].type == TokenType.TABLE:
            anchor, table_html = html_part.split("\n", 1)
            content = prompt.format(target_language=target_language, text_to_translate=table_html)
            response = get_translation(model, content)
            translated_html_parts.append(anchor + "\n" + response)
            continue
        if segments[index].type in {TokenType.TITLE, TokenType.SECTION_HEADER}:
            anchor, text = html_part.split("\n")
            content = prompt.format(target_language=target_language, text_to_translate=text)
            response = get_translation(model, content)
            translated_html_parts.append(anchor + "\n" + response)
            if extract_toc:
                title_segments.append(segments[index])
                title_segments[-1].text = response.replace("#", "").strip()
            continue
        if segments[index].type == TokenType.FORMULA:
            translated_html_parts.append(html_part)
            continue
        encoded_text, link_map, doc_ref_map = encode_html(html_part)
        content = prompt.format(target_language=target_language, text_to_translate=encoded_text)
        response = get_translation(model, content)
        translated_html_parts.append(decode_html(response, link_map, doc_ref_map))
    if extract_toc:
        translated_html_parts.insert(0, get_table_of_contents(title_segments))
    return "\n\n".join(translated_html_parts)


def translate_markup(
    output_format: OutputFormat,
    segments: list[SegmentBox],
    markup_parts: list[str],
    model: str,
    target_language: str,
    extract_toc: bool = False,
) -> str:
    if output_format == OutputFormat.MARKDOWN:
        return translate_markdown(segments, markup_parts, model, target_language, extract_toc)
    else:
        return translate_html(segments, markup_parts, model, target_language, extract_toc)
