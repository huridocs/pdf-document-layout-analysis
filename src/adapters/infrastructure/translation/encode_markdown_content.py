import re


def encode_markdown(text):
    link_map = []
    doc_ref_map = []
    bold_map = []
    italic_map = []
    bold_italic_map = []

    # Helper to encode links with nested brackets in label
    def link_replacer(match):
        label = match.group(1)[1:-1]  # Remove outer []
        url = match.group(3)  # Fixed: get the actual URL from group 3
        idx = len(link_map)
        link_map.append((label, url))
        return f"[LINK{idx}]{label}[LINK{idx}]"

    # Helper to encode doc refs
    def doc_ref_replacer(match):
        idx = len(doc_ref_map)
        doc_ref_map.append(match.group(0))
        return f"[DOCREF{idx}]"

    # Helper to encode bold+italic
    def bold_italic_replacer(match):
        text_content = match.group(1)
        idx = len(bold_italic_map)
        bold_italic_map.append(text_content)
        return f"[BI{idx}]{text_content}[BI{idx}]"

    # Helper to encode bold
    def bold_replacer(match):
        text_content = match.group(1)
        idx = len(bold_map)
        bold_map.append(text_content)
        return f"[B{idx}]{text_content}[B{idx}]"

    # Helper to encode italic
    def italic_replacer(match):
        text_content = match.group(1)
        idx = len(italic_map)
        italic_map.append(text_content)
        return f"[IT{idx}]{text_content}[IT{idx}]"

    # 1. Encode document references FIRST (multiple forms)
    text = re.sub(r"(\[(?:\\?\d+[,\.]? ?)+\]\(#page-\d+-\d+\))", doc_ref_replacer, text)
    text = re.sub(r"(\[\d+[,\.]?\]\(#page-\d+-\d+\))", doc_ref_replacer, text)
    text = re.sub(r"(\[\*\d+[,\.]?\]\(#page-\d+-\d+\))", doc_ref_replacer, text)  # Handle [*1221](#page-3-7) format

    # 2. Encode links BEFORE formatting to avoid matching underscores in URLs
    # This regex matches [label](url) where label can contain nested []
    link_pattern = re.compile(r"(\[((?:[^\[\]]+|\[[^\[\]]*\])*)\])\((https?://[^\)]+)\)")
    while True:
        new_text = link_pattern.sub(lambda m: link_replacer(m), text)
        if new_text == text:
            break
        text = new_text

    # 3. Encode bold+italic BEFORE individual bold/italic (**_text_** or __*text*__)
    text = re.sub(r"\*\*\_([^\*_]+)\_\*\*", bold_italic_replacer, text)
    text = re.sub(r"__\*([^\*_]+)\*__", bold_italic_replacer, text)

    # 4. Encode bold (**text** or __text__)
    text = re.sub(r"\*\*([^\*]+)\*\*", bold_replacer, text)
    text = re.sub(r"__([^\_]+)__", bold_replacer, text)

    # 5. Encode italic (_text_ or *text*) - now URLs are already encoded so no conflict
    text = re.sub(r"\_([^\_]+)\_", italic_replacer, text)
    text = re.sub(r"\*([^\*]+)\*", italic_replacer, text)

    return text, link_map, doc_ref_map
