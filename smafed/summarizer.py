import numpy as np

from helpers.rank_utils import make_array_of_tokens, split_on_tokens


class Summarizer:
    """
    Class for summarizing.
    """

    def __init__(self, tweets, dbworker, collection_with_precessed_tweets, tweets_grouped_by_cluster):
        """
        :param tweets: dictionary where key - tweet, value - cluster id.
        :param dbworker: object of database wrapper.
        :param collection_with_precessed_tweets: name of collection with processed tweets
        :param tweets_grouped_by_cluster: dictionary where key - cluster id and value - list of tweets in this cluster
        """
        self.tweets_cluster_dict = tweets
        self.clusters = np.arange(max(tweets.values()) + 1)

        # Database wrapper used here for loading tweets which already clustered and store in database.
        self.dbworker = dbworker
        self.collection = collection_with_precessed_tweets

        self.unique_in_all_clusters = None
        self.counts_in_all_clusters = None
        self.grouped_tweets = tweets_grouped_by_cluster
        self.grouped_tweets_with_scores = None

        self.init_function()

    def init_function(self):
        """
        Function for initialize fields which will be used in future for ranking
        and for getting data from database.
        """
        tokens_in_cluster = make_array_of_tokens(self.tweets_cluster_dict.keys())
        self.unique_in_all_clusters, self.counts_in_all_clusters = np.unique(tokens_in_cluster, return_counts=True)

    def summarize_clusters(self):
        """
        Function for summarize clusters.
        Clusters with tweets and theirs scores will be saved in self.grouped_tweets_with_scores dictionary.
        """
        self.grouped_tweets_with_scores = dict(zip(self.clusters, [0 for _ in range(len(self.clusters))]))
        for cluster, tweets in self.grouped_tweets.items():
            tweet_scores = self.compute_tweet_scores(tweets)
            self.grouped_tweets_with_scores[cluster] = dict(zip(tweets, tweet_scores))

    def compute_tweet_scores(self, tweets):
        """
        :param tweets: tweets in cluster.

        Return array of tweet scores.
        """
        tokens = make_array_of_tokens(tweets)
        unique_in_cluster, counts_in_cluster = np.unique(tokens, return_counts=True)
        weights = [self.compute_tweet_score(tweet, unique_in_cluster, counts_in_cluster) for tweet in tweets]
        return weights

    def compute_tweet_score(self, tweet, unique_in_cluster, counts_in_cluster):
        """
        :param tweet: single tweet.
        :param unique_in_cluster: unique words in cluster
        :param counts_in_cluster: counts of unique words in cluster

        Return score of single tweet.
        """
        xs = np.array(
            [counts_in_cluster[np.where(unique_in_cluster == word)] for word in split_on_tokens(tweet)]) + 1
        ys = np.array(
            [self.counts_in_all_clusters[np.where(self.unique_in_all_clusters == word)] for word in
             split_on_tokens(tweet)]) + 1
        ws = 0.5 * np.log(xs) + 0.5 * np.log(ys)
        return np.sum(ws)
