from smafed.cleaner import Cleaner
from nltk import pos_tag
from nltk.corpus import wordnet, stopwords
from nltk.stem import WordNetLemmatizer


class TweetTransformer(Cleaner):
    """
    Class for tweets transformation.
    """

    def __init__(self, sentences, num_of_tokens, entities=None):
        """
        :param sentences: sentences to cleaning (tweets).
        :param entities: entities in this sentences.
        :param num_of_tokens: minimum number of tokens
        """
        super().__init__(sentences, entities)
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = stopwords.words()
        self.num_of_tokens = num_of_tokens

    def preprocess(self):
        """
        Preprocess sentences:
        - clean sentences;
        - make tokenization;
        - make lemmatization;
        - drop stop words.
        """
        self.clean_sentences()
        tokens = [sentence.split(" ") for sentence in self.sentences]
        tokens = [self.lemmatize_sentence(sentence) for sentence in tokens]
        tokens = [self.drop_stop_words_in_sentence(sentence) for sentence in tokens]
        self.sentences = [" ".join(sentence) if len(sentence) >= self.num_of_tokens else "" for sentence in tokens]

    def lemmatize_sentence(self, sentence):
        """
        :param sentence: sentence to process.
        Make lemmatization for all words in sentence (list of tokens).
        """
        return [self.lemmatizer.lemmatize(word, TweetTransformer.get_wordnet_pos(word)) if word != "" else "" for word
                in sentence]

    def drop_stop_words_in_sentence(self, sentence):
        """
        :param sentence: sentence to process.
        Drop stop words in sentence (list of tokens).
        """
        return [word for word in sentence if word not in self.stop_words]

    @staticmethod
    def get_wordnet_pos(word):
        """
        :param word: word
        :return: word`s part of speech
        """
        tag = pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)
