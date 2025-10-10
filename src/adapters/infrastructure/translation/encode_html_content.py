import re


def encode_html(text):
    text = text.replace("</i> <i>", " ")

    link_map = []
    doc_ref_map = []
    bold_map = []
    italic_map = []
    bold_italic_map = []

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

    # 1. Encode document references FIRST - Updated patterns to match your actual format
    # Handle patterns like [\[9,](#page-5-9), [10,](#page-5-10), [11\]](#page-5-11), [\[12\]](#page-5-12), [\[13\]](#page-5-13)
    text = re.sub(r"(\[\\?\[?\*?\d+[,\.]?\\?\]?\]\(#page-\d+-\d+\))", doc_ref_replacer, text)

    # Also handle the original patterns from markdown version
    text = re.sub(r"(\[(?:\\?\d+[,\.]? ?)+\]\(#page-\d+-\d+\))", doc_ref_replacer, text)
    text = re.sub(r"(\[\d+[,\.]?\]\(#page-\d+-\d+\))", doc_ref_replacer, text)
    text = re.sub(r"(\[\*\d+[,\.]?\]\(#page-\d+-\d+\))", doc_ref_replacer, text)

    # 2. Encode links BEFORE formatting - handle complex nested structures
    def find_and_replace_links(text):
        offset = 0  # Track how much the text has shifted due to replacements

        # Find all <a href="..." tags
        pattern = r'<a\s+href=["\']([^"\']+)["\'][^>]*>'
        matches = list(re.finditer(pattern, text, re.IGNORECASE))

        # Process from left to right
        for match in matches:
            start = match.start() + offset
            href = match.group(1)

            # Find the matching closing </a> tag
            tag_count = 1
            pos = match.end() + offset
            content_start = pos

            while pos < len(text) and tag_count > 0:
                # Look for opening <a> tags
                next_open = text.find("<a ", pos)
                next_open_case = text.find("<A ", pos)
                if next_open_case != -1 and (next_open == -1 or next_open_case < next_open):
                    next_open = next_open_case

                # Look for closing </a> tags
                next_close = text.find("</a>", pos)
                next_close_case = text.find("</A>", pos)
                if next_close_case != -1 and (next_close == -1 or next_close_case < next_close):
                    next_close = next_close_case

                if next_close == -1:
                    break

                if next_open != -1 and next_open < next_close:
                    # Found nested opening tag
                    tag_count += 1
                    pos = next_open + 3
                else:
                    # Found closing tag
                    tag_count -= 1
                    if tag_count == 0:
                        # This is our matching closing tag
                        content = text[content_start:next_close]
                        end = next_close + 4  # +4 for </a>

                        # Replace the entire link
                        idx = len(link_map)
                        link_map.append((content, href))
                        replacement = f"[LINK{idx}]{content}[LINK{idx}]"

                        original_length = end - start
                        new_length = len(replacement)

                        text = text[:start] + replacement + text[end:]
                        offset += new_length - original_length
                        break
                    else:
                        pos = next_close + 4

        return text

    text = find_and_replace_links(text)

    # 3. Encode bold+italic combinations BEFORE individual bold/italic
    # Handle <b><i>text</i></b> and <i><b>text</b></i> - only simple cases without nested links
    text = re.sub(r"<b><i>([^<]+)</i></b>", bold_italic_replacer, text, flags=re.IGNORECASE)
    text = re.sub(r"<i><b>([^<]+)</b></i>", bold_italic_replacer, text, flags=re.IGNORECASE)

    # 4. Encode bold (<b>text</b>) - only simple cases without nested tags
    text = re.sub(r"<b>([^<]+)</b>", bold_replacer, text, flags=re.IGNORECASE)

    # 5. Encode italic (<i>text</i>) - handle cases that might contain encoded links
    def italic_with_links_replacer(match):
        content = match.group(1)
        idx = len(italic_map)
        italic_map.append(content)
        return f"[IT{idx}]{content}[IT{idx}]"

    # Handle italic tags that might contain encoded links
    text = re.sub(
        r"<i>([^<]*(?:\[LINK\d+\][^\[]*\[LINK\d+\][^<]*)*)</i>", italic_with_links_replacer, text, flags=re.IGNORECASE
    )
    # Handle simple italic tags
    text = re.sub(r"<i>([^<]+)</i>", italic_with_links_replacer, text, flags=re.IGNORECASE)

    return text, link_map, doc_ref_map
