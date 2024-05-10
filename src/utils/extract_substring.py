def extract_substring(text, start, end):
    start_index = text.find(start) + len(start)
    end_index = text.find(end)
    if start_index > -1 and end_index > -1:
        return text[start_index:end_index].strip()
    return ""
