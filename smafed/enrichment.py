import numpy as np
import re

from nltk.corpus import wordnet
from sklearn.metrics.pairwise import cosine_similarity


class EnrichmentLayer:
    """
    Tweets enrichment class

    EnrichmentLayer is class which searches slang words in tweets and replaces it on their most
    similar definitions in IKB mongo DB
    """

    def __init__(self, model=None, database=None, collection_of_slangs=None, collection_processed=None,
                 collection_used_slang=None,
                 spell_correct=None):
        self.model = model
        """sent2vec model instance"""
        self.database = database
        """database name"""
        self.collection_of_slangs = collection_of_slangs
        """slangs collection name"""
        self.collection_processed = collection_processed
        """name of collection with processed tweets"""
        self.collection_used_slang = collection_used_slang
        """name of collection with used slangs"""
        self.spell_correct = spell_correct
        """spell corrector instance"""

    @staticmethod
    def extract_def_use(elements):
        """
        extracts definition and usages fro elements of dictionaries
        :param elements: list of dicts with definitions and usages of slang

        Return definition and usage of slang
        """

        definition_usage_tuple = [(definition, usage) for element in elements for i, (definition, usage) in
                                  enumerate(zip(element['definition'], element['usage'])) if
                                  len(definition) != 0 and len(usage) != 0 and definition != "" and usage != ""]
        definitions = [el[0] for el in definition_usage_tuple]
        usages = [el[1] for el in definition_usage_tuple]
        definitions = [re.sub(r'[\n\r\t]', ' ', el) for el in definitions]
        usages = [re.sub(r'[\n\r\t]', ' ', el) for el in usages]
        return definitions, usages

    @staticmethod
    def replace_word(tokens, word, definition):
        """
        inserts definition instead slang word
        :param tokens: tokens of tweet
        :param word: word to be checked
        :param definition: definition of slang from IKB
        Return tweet with inserted definition
        """
        try:
            ind = tokens.index(word)
            try:
                new_tokens = tokens[:ind] + definition.split(' ') + tokens[ind + 1:]
            except IndexError:
                new_tokens = tokens[:ind] + definition.split(' ')
            return " ".join(new_tokens)
        except ValueError:
            return " ".join(tokens)

    def spell_correction(self, tweet):
        """
        corrects spelling in tweet
        :param tweet: sentence as string to be corrected

        Return tweet with corrected spelling
        """
        return self.spell_correct.correct(tweet)

    def lesk(self, tweet, word, created_at, tweet_id):
        """
        Lesk algorithm for finding best definition of slang word in tweet
        :param tweet: tweet in which slangs will be replaced
        :param word: slang word of tweet that will be replaced on definition from IKB
        :param created_at: time of tweet creation
        :param tweet_id: tweet id

        Return enriched tweet, used definition
        """
        ikb_obj = self.database.get(self.collection_of_slangs, field='word', value=word)[0]
        ikb_id = ikb_obj["_id"]

        dicts = ikb_obj['payload']
        elements = [value for dictt, item in dicts.items() for value in item]
        definitions, usages = self.extract_def_use(elements)
        if len(definitions) == 0:
            raise ValueError("Empty lists of definitions and usages")
        usages_vec = self.model.vectorize_sentences(usages)
        tweet_vec = self.model.vectorize_sentences([tweet])
        cs = np.array(cosine_similarity(usages_vec, tweet_vec))
        ind_max = np.argmax(cs)

        best_definition = definitions[ind_max]
        dictionary_of_best_definition = EnrichmentLayer.find_name_of_dict_by_definition(dicts, best_definition)
        try:
            filter_for_search = {"dictionary_title": dictionary_of_best_definition, "definition": best_definition}
            document = self.database.get(self.collection_used_slang, filter=filter_for_search)[0]
            tweets = document['tweets']
            tweets.append(tweet_id)
            self.database.update(self.collection_used_slang, "ikb_id", ikb_id, {"tweets": tweets}, upsert=False)
            id_of_insert = document['_id']
        except IndexError:
            document = {'ikb_id': ikb_id, 'word': word, 'dictionary_title': dictionary_of_best_definition,
                        'definition': best_definition, 'created_at': created_at, 'tweets': [tweet_id]}
            id_of_insert = self.database.insert(self.collection_used_slang, document)

        return self.replace_word(tweet.split(), word, best_definition), best_definition, id_of_insert

    def tweet_enrichment(self, tweet):
        """
        Method that enriches tweet with best definition from IKB and makes spell correction,
        saves enriched_tweet, tweet_id, slangs and definitions used in tweet to database
        :param tweet: tweet to be enriched
        Return dictionary {tweet_id: enriched tweet}
        """
        d = {}
        slangs = []
        definitions = []
        used_slang_ids = []
        text = tweet['cleaned'].split()
        for word in text:
            if word not in wordnet.words():
                try:
                    enriched, definition, insert_slang_id = self.lesk(tweet['cleaned'], word, tweet["created_at"],
                                                                      tweet['tweet_id'])
                    d[word] = definition
                    slangs.append(word)
                    used_slang_ids.append(insert_slang_id)
                    definitions.append(definition)
                except (IndexError, ValueError) as e:
                    pass
        for word, definition in d.items():
            ind = text.index(word)
            text[ind] = definition
        enriched_tweet = ' '.join(text)
        enriched_tweet = self.spell_correction(enriched_tweet)
        tweet['enriched_tweet'], tweet['used_slang_ids'] = enriched_tweet, used_slang_ids
        tweet.pop('cleaned')
        if not self.database.get(self.collection_processed, "enriched_tweet", tweet['enriched_tweet']).count() > 0:
            self.database.insert(self.collection_processed, tweet)
            return {tweet['tweet_id']: tweet['enriched_tweet']}
        else:
            return None

    def tweets_enrichment(self, tweets):
        """
        Method that enriches tweet in list of tweets with best definition from IKB and makes spell correction
        :param tweets: list of tweets to be enriched

        Return dictionary {tweet_id: enriched tweet}
        """
        tweet_dict = {}
        for tweet in tweets:
            new_tweet = self.tweet_enrichment(tweet)
            if new_tweet:
                tweet_dict.update(new_tweet)
        return tweet_dict

    @staticmethod
    def find_name_of_dict_by_definition(dicts, definition):
        for key, value in dicts.items():
            definitions_in_dict = [element['definition'][0] for element in value]
            try:
                definitions_in_dict.index(definition)
                return key
            except ValueError:
                pass
