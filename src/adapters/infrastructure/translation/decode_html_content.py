import re


def decode_html(text, link_map, doc_ref_map):
    # 1. Decode bold+italic first
    def bold_italic_decoder(match):
        return f"<b><i>{match.group(2)}</i></b>"

    text = re.sub(r"\[BI(\d+)\](.*?)\[BI\1\]", bold_italic_decoder, text)

    # 2. Decode bold
    def bold_decoder(match):
        return f"<b>{match.group(2)}</b>"

    text = re.sub(r"\[B(\d+)\](.*?)\[B\1\]", bold_decoder, text)

    # 3. Decode italic
    def italic_decoder(match):
        return f"<i>{match.group(2)}</i>"

    text = re.sub(r"\[IT(\d+)\](.*?)\[IT\1\]", italic_decoder, text)

    # 4. Decode links
    def link_decoder(match):
        idx = int(match.group(1))
        if idx < len(link_map):
            label, url = link_map[idx]
            return f'<a href="{url}">{match.group(2)}</a>'
        else:
            # Return original text if index is out of range
            return match.group(0)

    text = re.sub(r"\[LINK(\d+)\](.*?)\[LINK\1\]", link_decoder, text)

    # 5. Decode doc refs (same as markdown since they're custom)
    def doc_ref_decoder(match):
        idx = int(match.group(1))
        if idx < len(doc_ref_map):
            return doc_ref_map[idx]
        else:
            # Return original text if index is out of range
            return match.group(0)

    text = re.sub(r"\[DOCREF(\d+)\]", doc_ref_decoder, text)
    text = text.replace("] (#page", "](#page")
    text = " ".join(text.split())

    return text
