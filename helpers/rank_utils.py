def split_on_tokens(sentence, separator=" "):
    """
    :param sentence: sentence which have to be split by separator
    :param separator: separator of sentence`s words
    """
    return sentence.split(separator)


def make_array_of_tokens(array_of_sentences):
    """
    :param array_of_sentences: array of sentences which have to be split on tokens

    Return array of tokens.
    """
    array_of_sentences = " ".join(array_of_sentences)
    return split_on_tokens(array_of_sentences)
