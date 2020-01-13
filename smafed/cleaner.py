import re


class Cleaner:
    """
    Class for data cleaning.
    """

    def __init__(self, sentences, entities):
        """
        :param  sentences: sentences to cleaning.
        :param entities: entities in this sentences.
        """
        self.sentences = Cleaner.sentences_to_lower(sentences)
        self.sentences_entities = entities

    @staticmethod
    def sentences_to_lower(sentences):
        """
        :param sentences: sentences to process.

        Return sentences in lowercase.
        """
        return [sentence.lower() for sentence in sentences]

    def clean_sentences(self):
        """
        Clean sentences:
        - replace entities by space;
        - remove punctuation;
        - remove repeating characters.
        """
        self.sentences = self.entities_replacement()
        self.sentences = self.punctuation_remove()
        self.sentences = self.repeating_characters_remove()

    def entities_replacement(self):
        """
        Replace entities from sentences by space.
        """
        sentences_without_entities = []
        for sentence, entity in zip(self.sentences, self.sentences_entities):
            for enitity_key, entity_value in entity.items():
                sentence = Cleaner.entity_in_sentence_replacement(sentence, entity_value)
            sentences_without_entities.append(sentence)
        return sentences_without_entities

    @staticmethod
    def entity_in_sentence_replacement(sentence, list_of_entity_in_sentence):
        """
        :param sentence: sentence to process
        :param list_of_entity_in_sentence: list of entity in sentence

        Replace entities from list_of_entity_in_sentence in sentence by space.
        """
        if len(list_of_entity_in_sentence) != 0:
            for element in list_of_entity_in_sentence:
                start = element['indices'][0]
                finish = element['indices'][1]
                sentence = sentence[:start] + (" " * (finish - start)) + sentence[finish:]
        return sentence

    def punctuation_remove(self):
        """
        Remove all punctuation signs, digits, and replace excessive spaces by single space.
        """
        sentences = [sentence.replace("&lt;", " ") for sentence in self.sentences]
        sentences = [sentence.replace("&gt;", " ") for sentence in sentences]
        sentences = [sentence.replace("&amp;", " ") for sentence in sentences]
        sentences = [Cleaner.replace_in_str(sentence, r'[^a-zA-Z0-9]', " ") for sentence in sentences]
        sentences = [Cleaner.replace_in_str(sentence, r"\d", " ") for sentence in sentences]
        sentences = [Cleaner.replace_in_str(sentence, r" {2,}", " ") for sentence in sentences]
        sentences = [Cleaner.replace_in_str(sentence, r"^ ", "") for sentence in sentences]
        sentences = [Cleaner.replace_in_str(sentence, r" $", "") for sentence in sentences]
        return sentences

    @staticmethod
    def replace_in_str(sentence, pattern, replace_by):
        """
        :param sentence: sentence in which replace
        :param pattern: pattern which have to be replaced
        :param replace_by: text fragment which replace
        """
        return re.sub(pattern, replace_by, sentence)

    def repeating_characters_remove(self):
        """
        Remove repeating characters using regular expression.
        Return array with sentences in which characters cannot be repeated more than twice.
        """
        result = []
        for sentence in self.sentences:
            result.append(" ".join([Cleaner.replace_in_str(word, r"(.)\1+", r"\1\1") for word in sentence.split(" ")]))
        return result
