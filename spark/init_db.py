import json
import os

from pymongo import HASHED


def mongo_init(connection):
    DATABASE_NAME = os.getenv("DATABASE_NAME", "event_detection_db")
    INPUT_TWEETS_COLLECTION_NAME = os.getenv("INPUT_TWEETS_COLLECTION_NAME", "tweets_input")
    IKB_COLLECTION_NAME = os.getenv("IKB_COLLECTION_NAME", "IKB")
    PROCESSED_TWEET_COLLECTION_NAME = os.getenv("PROCESSED_TWEET_COLLECTION_NAME", "tweets_processed")
    CLUSTER_COLLECTION_NAME = os.getenv("CLUSTER_COLLECTION_NAME", "cluster")
    USED_SLANG_COLLECTION_NAME = os.getenv("USED_SLANG_COLLECTION_NAME", "used_slang")

    with open("IKB.json") as file:
        data = json.load(file)
    connection[DATABASE_NAME][IKB_COLLECTION_NAME].insert(data)
    with open("tweets_processed_init.json") as file:
        data = json.load(file)
    connection[DATABASE_NAME][PROCESSED_TWEET_COLLECTION_NAME].insert(data)
    with open("tweets_input_init.json") as file:
        data = json.load(file)
    connection[DATABASE_NAME][INPUT_TWEETS_COLLECTION_NAME].insert(data)
    with open("cluster_init.json") as file:
        data = json.load(file)
    connection[DATABASE_NAME][CLUSTER_COLLECTION_NAME].insert(data)
    with open("used_slang_init.json") as file:
        data = json.load(file)
    connection[DATABASE_NAME][USED_SLANG_COLLECTION_NAME].insert(data)
    connection[DATABASE_NAME][IKB_COLLECTION_NAME].create_index([("word", HASHED)], name="word_hashed")
    connection[DATABASE_NAME][INPUT_TWEETS_COLLECTION_NAME].create_index([("tweet_id", HASHED)], name="tweet_id_hashed")
    connection[DATABASE_NAME][PROCESSED_TWEET_COLLECTION_NAME].create_index([("tweet_id", HASHED)],
                                                                            name="tweet_id_hashed")
    connection[DATABASE_NAME][PROCESSED_TWEET_COLLECTION_NAME].create_index([("init", HASHED)], name="init_hashed")
    connection[DATABASE_NAME][PROCESSED_TWEET_COLLECTION_NAME].create_index([("cluster", HASHED)],
                                                                            name="cluster_hashed")
    connection[DATABASE_NAME][CLUSTER_COLLECTION_NAME].create_index([("cluster", HASHED)], name="cluster_hashed")
    connection[DATABASE_NAME][USED_SLANG_COLLECTION_NAME].create_index([("definition", HASHED)],
                                                                       name="definition_hashed")
    connection[DATABASE_NAME][USED_SLANG_COLLECTION_NAME].create_index([("dictionary_title", HASHED)],
                                                                       name="dictionary_title_hashed")

    connection[DATABASE_NAME][INPUT_TWEETS_COLLECTION_NAME].remove({})
    connection[DATABASE_NAME][PROCESSED_TWEET_COLLECTION_NAME].remove({})
    connection[DATABASE_NAME][CLUSTER_COLLECTION_NAME].remove({})
    connection[DATABASE_NAME][USED_SLANG_COLLECTION_NAME].remove({})
