import numpy as np

from helpers.rank_utils import make_array_of_tokens


class Ranker:
    """
    Class for ranking.
    """

    def __init__(self, tweets, dbworker, collection_with_precessed_tweets):
        """
        :param tweets: dictionary where key - tweet, value - cluster id.
        :param dbworker: object of database wrapper.
        :param collection_with_precessed_tweets: name of collection with processed tweets
        """
        self.tweets_cluster_dict = tweets
        self.clusters = np.arange(max(tweets.values()) + 1)

        # Database wrapper used here for loading tweets which already clustered and store in database.
        self.dbworker = dbworker
        self.collection = collection_with_precessed_tweets

        self.cluster_scores = {}
        self.grouped_tweets = None

        self.init_function()

    def init_function(self):
        """
        Function for initialize fields which will be used in future for ranking
        and for getting data from database.
        """
        for i in range(len(self.clusters)):
            for tweet_obj in self.dbworker.get(self.collection, "cluster", i):
                self.tweets_cluster_dict[tweet_obj["enriched_tweet"]] = i
        self.grouped_tweets = self.group_by_clusters()

    def ranking_cluster(self):
        """
        Function for cluster ranking.
        Cluster scores will be saved in self.cluster_scores array.
        """
        for cluster, tweets in self.grouped_tweets.items():
            if Ranker.not_empty(tweets):
                self.cluster_scores[cluster] = Ranker.compute_cluster_score(tweets)

    @staticmethod
    def not_empty(array):
        """
        :param array: array to checking.

        Return True if list is empty.
        """
        return len(array) != 0

    def group_by_clusters(self):
        """
        Group tweets by cluster.

        Return dictionary where key - cluster, value - array of tweets.
        """
        result_d = dict(zip(self.clusters, [[] for _ in range(len(self.clusters))]))
        for key, value in self.tweets_cluster_dict.items():
            result_d[value].append(key)
        return result_d

    @staticmethod
    def compute_cluster_score(tweets):
        """
        :param tweets: tweets in cluster.

        Return cluster score.
        """
        tokens = make_array_of_tokens(tweets)
        unique, counts = np.unique(tokens, return_counts=True)
        weight_of_words = [np.log(counts[np.where(unique == word)] + 1) for word in tokens]
        return np.sum(weight_of_words)
