import os
import pickle

from datetime import datetime
from helpers.mongodb_worker import MongoDBWorker

DATABASE_NAME = os.getenv("DATABASE_NAME", "event_detection_db")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", '27017'))

PROCESSED_TWEETS_COLLECTION_NAME = os.getenv("PROCESSED_TWEETS_COLLECTION_NAME", "tweets_processed")
CLUSTER_COLLECTION_NAME = os.getenv("CLUSTER_COLLECTION_NAME", "cluster")
PATH = os.path.dirname(os.path.abspath(__file__))


def diff_in_time_more_than_month(time, current_time):
    return (current_time - time).days >= 4


def delete_clusters():
    time_script_running = datetime.now()
    dbworker = MongoDBWorker(DATABASE_NAME, DATABASE_HOST, DATABASE_PORT)
    with open(os.path.join(PATH, "data_smafed", "cluster", "clusters_creating_time.pcl"), "rb") as file:
        cluster_creating_time = pickle.load(file)
        cluster_to_delete = [key for key, value in cluster_creating_time.items() if
                             diff_in_time_more_than_month(value, time_script_running)]
        if len(cluster_to_delete) != 0:
            for cluster in cluster_to_delete:
                try:
                    os.remove(os.path.join(PATH, "data_smafed", "cluster", f"{cluster}.pcl"))
                except FileNotFoundError:
                    pass
                cluster_creating_time.pop(cluster)
                for tweet in dbworker.get(PROCESSED_TWEETS_COLLECTION_NAME, "cluster", cluster):
                    dbworker.delete(PROCESSED_TWEETS_COLLECTION_NAME, "tweet_id", tweet['tweet_id'])
                dbworker.delete(CLUSTER_COLLECTION_NAME, "cluster", cluster)
    with open(os.path.join(PATH, "data_smafed", "cluster", "clusters_creating_time.pcl"), "wb") as file:
        pickle.dump(cluster_creating_time, file)
