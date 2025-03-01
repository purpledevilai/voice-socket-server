def first_occurrence_end(text, substrings):
    indices = [(text.find(sub) + len(sub))
               for sub in substrings if text.find(sub) != -1]
    # Return the lowest index, or -1 if no match is found
    return min(indices) if indices else -1


def sentence_stream(token_generator):
    text = ''
    for token in token_generator:
        text += token
        split_index = first_occurrence_end(
            text, [". ", "! ", "? ", ".\n", "!\n", "?\n"])
        if (split_index != -1):
            yield text[:split_index]
            text = text[split_index:]
    yield text
