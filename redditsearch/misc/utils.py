def find_text_in_between_tags(text, start_tag, end_tag):
    start_pos = text.find(start_tag)
    end_pos = text.find(end_tag)
    text_between_tags = text[start_pos + len(start_tag): end_pos]

    return text_between_tags