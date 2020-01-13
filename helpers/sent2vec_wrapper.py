from sent2vec import Sent2vecModel


class Sent2VecWrapper:
    """
    Wrapper for sent2vec object.
    """

    def __init__(self, path_to_model):
        self.model = Sent2vecModel()
        self.model.load_model(path_to_model)

    def vectorize_sentences(self, sentences):
        """
        :param sentences: sentences to vectorize

        Return array of vectorized sentences.
        """
        return self.model.embed_sentences(sentences)
