import json

from pandas import DataFrame
from datetime import datetime


def timestamp_from_str(string):
    format = "%a %b %d %H:%M:%S %z %Y"
    return datetime.strptime(string, format)


def collect_data_for_enriched(df_init, cleaned):
    """
    :param df_init: input dataframe. Contain text of tweet, date of its posting and entities in it.
    :param cleaned: tweets after preprocessing.

    Return json array each element of which is dictionary with keys:
    - init - init text of tweet;
    - cleaned - text of tweet after preprocessing;
    - created_at - date of tweet posting;
    - tweet_id - tweets id.
    """

    df_init["cleaned"] = cleaned

    df_init = df_init.drop(["entities"], axis=1)
    df_init = df_init[df_init['cleaned'] != ""]

    json_array = json.loads(df_init.to_json(orient='records'))
    for i in range(len(json_array)):
        json_array[i]['created_at'] = timestamp_from_str(json_array[i]['created_at'])

    return json_array


def save_in_db_clusters_staff(dbworker, collection, cluster_dict, field_name):
    """
    :param dbworker: object of database wrapper.
    :param collection: collection in which save data.
    :param cluster_dict: dict where key - cluster id, value - value for saving.
    :param field_name: field where new value must be saving

    Save in database cluster with values from cluster_dict item.
    """
    for key, value in cluster_dict.items():
        dbworker.update(collection, "cluster", int(key), {field_name: value}, upsert=True)


def save_in_db_tweets_score_and_cluster(dbworker, collection, dict_enriched_tweets, clusters_array,
                                        grouped_tweets_with_scores):
    """
    :param dbworker: object of database wrapper.
    :param collection: collection in which save data.
    :param dict_enriched_tweets: dict where key - tweet id, value - score of this tweet.
    :param clusters_array: array of cluster which is related to tweet ids sequence
    :param grouped_tweets_with_scores: dict where key - cluster id, value - tuple with tweet and its score.

    Save tweets cluster and score into database.
    """
    for (tweet_id, tweet), cluster in zip([(key, value) for key, value in dict_enriched_tweets.items()],
                                          clusters_array):
        score = grouped_tweets_with_scores[cluster][tweet]
        update = {"score": score, "cluster": cluster}
        dbworker.update(collection, "tweet_id", tweet_id, update)


def load_data_from_db(dbworker, collection):
    """
    :param dbworker: object of database wrapper.
    :param collection: collection in which data store.

    Load and delete data from collection into dataframe.
    If data don`t exist return empty dataframe.
    """
    data = DataFrame()
    for document in dbworker.get(collection):
        data = data.append(document, ignore_index=True)
        dbworker.delete(collection, "_id", document['_id'])
    try:
        data = data.drop(["_id"], axis=1)
    except KeyError:
        pass
    return data


def save_word_score(tweets_grouped_by_cluster, dbworker, collection):
    """
    :param tweets_grouped_by_cluster: dictionary in which key - cluster id, value - tweets in this cluster.
    :param dbworker: object of database wrapper.
    :param collection: collection in which data store.

    Save top 20 words of each cluster into database in match with this cluster.
    """
    cluster_sentences = dict(zip(tweets_grouped_by_cluster.keys(),
                                 [" ".join(sentences) for sentences in tweets_grouped_by_cluster.values()]))
    for cluster, sentence in cluster_sentences.items():
        d = {}
        tokens = sentence.split()
        uniq_words = sorted(set(tokens))
        for word in uniq_words:
            d[word] = tokens.count(word)
        for key in d:
            d[key] = d[key] / max(d.values())
        words = dict(sorted(d.items(), key=lambda x: x[1], reverse=True)[:20])
        if len(words) != 0:
            dbworker.update(collection, "cluster", int(cluster), {"words": words}, upsert=True)
