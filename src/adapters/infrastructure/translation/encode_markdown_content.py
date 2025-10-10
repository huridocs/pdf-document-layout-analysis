import re


def encode_markdown(text):
    text = text.replace("_ _", " ")

    link_map = []
    doc_ref_map = []
    bold_map = []
    italic_map = []
    bold_italic_map = []

    # Helper to encode links with nested brackets in label
    def link_replacer(match):
        label = match.group(1)[1:-1]  # Remove outer []
        url = match.group(3)
        idx = len(link_map)
        link_map.append((label, url))
        return f"[LINK{idx}]{label}[LINK{idx}]"

    # Helper to encode doc refs - sequential numbering
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

    # 1. Encode ALL document references in ONE PASS for sequential numbering
    doc_ref_patterns = [
        r"\[\\?\[\d+,\]\(#page-\d+-\d+\)",  # [\[9,](#page-5-9)
        r"\[\\?\[\d+\\?\]\]\(#page-\d+-\d+\)",  # [\[12\]](#page-5-12)
        r"\[\*\d+\]\(#page-\d+-\d+\)",  # [*1221](#page-3-7)
        r"\[\d+,\]\(#page-\d+-\d+\)",  # [10,](#page-5-10)
        r"\[\d+\\?\]\]\(#page-\d+-\d+\)",  # [11\]](#page-5-11)
        r"\[\d+\]\(#page-\d+-\d+\)",  # [1221](#page-3-7)
    ]

    # Combine all patterns with alternation (|)
    combined_pattern = "(" + "|".join(doc_ref_patterns) + ")"
    text = re.sub(combined_pattern, doc_ref_replacer, text)

    # 2. Encode links BEFORE formatting to avoid matching underscores in URLs
    link_pattern = re.compile(r"(\[((?:[^\[\]]+|\[[^\[\]]*\])*)\])\((https?://[^\)]+)\)")
    while True:
        new_text = link_pattern.sub(lambda m: link_replacer(m), text)
        if new_text == text:
            break
        text = new_text

    # 3. Encode bold+italic BEFORE individual bold/italic
    text = re.sub(r"\*\*\_([^\*_]+)\_\*\*", bold_italic_replacer, text)
    text = re.sub(r"_\*([^\*_]+)\*_", bold_italic_replacer, text)

    # 4. Encode bold
    text = re.sub(r"\*\*([^\*]+)\*\*", bold_replacer, text)

    # 5. Encode italic
    text = re.sub(r"\_([^\_]+)\_", italic_replacer, text)

    return text, link_map, doc_ref_map
