from adapters.infrastructure.markup_conversion.OutputFormat import OutputFormat
from adapters.infrastructure.translation.decode_html_content import decode_html
from adapters.infrastructure.translation.decode_markdown_content import decode_markdown
from adapters.infrastructure.translation.encode_html_content import encode_html
from adapters.infrastructure.translation.encode_markdown_content import encode_markdown
from adapters.infrastructure.translation.ollama_container_manager import OllamaContainerManager
from configuration import service_logger
from domain.SegmentBox import SegmentBox
from pdf_token_type_labels.TokenType import TokenType
from tqdm import tqdm

prompt = """You are a professional translator. Your task is to translate the following text to {target_language}.

**CRITICAL: You must output ONLY the {target_language} translation. Do NOT repeat the source text.**
    
    
Follow these guidelines:

1. Translate all text accurately without omitting any part of the content.
2. Preserve the tone and style of the original text.
3. Do not change, remove, or add any markdown symbols (such as *, _, #, [ ], ( ), -, or backticks). Only translate the visible text.
4. Do not translate person names, URLs, email addresses, or code snippets. Only translate the human-readable text.
5. Make sure that you are returning the translation, not the source text.
6. If you see custom tags (such as [DOC_REF], [IT], [B], [LINK]), **translate the text inside the tags, but do not change, remove, or translate the tags themselves.** The tags must appear in the same positions in the output as in the input.
7. If a word is split with a hyphen (e.g., "sec- onds"), treat it as a single word, get rid of the hyphen and translate it as one complete word in the target language.
8. Do not include any additional comments, notes, or explanations in the output; provide only the translated text.

**IMPORTANT: The text between the backticks below is the source text. You must output the {target_language} translation, NOT the source.**

Here is the text to be translated:

```
{text_to_translate}
```
"""


def get_translation(ollama_manager: OllamaContainerManager, model: str, content: str, source_markup: str) -> str:
    response = ollama_manager.chat_with_timeout(
        model=model, messages=[{"role": "user", "content": content}], source_markup=source_markup
    )

    if response is None:
        raise Exception("Translation request failed or timed out")

    if isinstance(response, str):
        return response

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
    ollama_manager: OllamaContainerManager,
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
    ten_percent_of_segments = len(markdown_parts) // 10
    service_logger.info(f"Starting translation of {len(markdown_parts)} segments")
    for index, markdown_part in tqdm(enumerate(markdown_parts), total=len(markdown_parts), desc="Translating markdown"):
        if index % ten_percent_of_segments == 0:
            service_logger.info("")
        markdown_part = markdown_part.strip()
        if not markdown_part:
            continue
        if segments[index].type == TokenType.PICTURE:
            translated_markdown_parts.append(markdown_part)
            continue
        if segments[index].type == TokenType.TABLE:
            anchor, table_html = markdown_part.split("\n", 1)
            content = prompt.format(target_language=target_language, text_to_translate=table_html)
            response = get_translation(ollama_manager, model, content, markdown_part)
            translated_markdown_parts.append(anchor + "\n" + response)
            continue
        if segments[index].type in {TokenType.TITLE, TokenType.SECTION_HEADER}:
            anchor, text = markdown_part.split("\n")
            content = prompt.format(target_language=target_language, text_to_translate=text)
            response = get_translation(ollama_manager, model, content, markdown_part)
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
        response = get_translation(ollama_manager, model, content, markdown_part)
        translated_markdown_parts.append(decode_markdown(response, link_map, doc_ref_map))
    service_logger.info("\033[92mTranslation of markdown segments completed\033[0m")
    if extract_toc:
        translated_markdown_parts.insert(0, get_table_of_contents(title_segments))
    return "\n\n".join(translated_markdown_parts)


def translate_html(
    ollama_manager: OllamaContainerManager,
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
    ten_percent_of_segments = len(html_parts) // 10
    service_logger.info(f"Starting translation of {len(html_parts)} segments")
    for index, html_part in tqdm(enumerate(html_parts), total=len(html_parts), desc="Translating html"):
        if index % ten_percent_of_segments == 0:
            service_logger.info("")
        html_part = html_part.strip()
        if not html_part:
            continue
        if segments[index].type == TokenType.PICTURE:
            translated_html_parts.append(html_part)
            continue
        if segments[index].type == TokenType.TABLE:
            anchor, table_html = html_part.split("\n", 1)
            content = prompt.format(target_language=target_language, text_to_translate=table_html)
            response = get_translation(ollama_manager, model, content, html_part)
            translated_html_parts.append(anchor + "\n" + response)
            continue
        if segments[index].type in {TokenType.TITLE, TokenType.SECTION_HEADER}:
            anchor, text = html_part.split("\n")
            content = prompt.format(target_language=target_language, text_to_translate=text)
            response = get_translation(ollama_manager, model, content, html_part)
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
        response = get_translation(ollama_manager, model, content, html_part)
        translated_html_parts.append(decode_html(response, link_map, doc_ref_map))
    service_logger.info("\033[92mTranslation of html segments completed\033[0m")
    if extract_toc:
        translated_html_parts.insert(0, get_table_of_contents(title_segments))
    return "\n\n".join(translated_html_parts)


def translate_markup(
    ollama_manager: OllamaContainerManager,
    output_format: OutputFormat,
    segments: list[SegmentBox],
    markup_parts: list[str],
    model: str,
    target_language: str,
    extract_toc: bool = False,
) -> str:
    if output_format == OutputFormat.MARKDOWN:
        return translate_markdown(ollama_manager, segments, markup_parts, model, target_language, extract_toc)
    else:
        return translate_html(ollama_manager, segments, markup_parts, model, target_language, extract_toc)
