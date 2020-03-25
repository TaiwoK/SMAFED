import json
import os

from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext

from init_db import mongo_init

TWITTER_PORT = int(os.getenv("TWITTER_PORT", '9009'))
DATABASE_PORT = int(os.getenv("PORT_DATABASE", '27017'))
HOST_NAME_TWITTER = os.getenv("HOST_NAME_TWITTER", "localhost")
HOST_NAME_DATABASE = os.getenv("HOST_NAME_DATABASE", "localhost")
DATABASE_NAME = os.getenv("DATABASE_NAME", "event_detection_db")
INPUT_TWEETS_COLLECTION_NAME = os.getenv("INPUT_TWEETS_COLLECTION_NAME", "tweets_input")
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'admin')
DATABASE_USER= os.getenv('DATABASE_USER', 'admin')
DATABASE_AUTHDB= os.getenv('DATABASE_AUTHDB', 'admin')

def filter_tweets(tweet):
    """
    :param tweet: json from twitter API

    If tweet is relevant return True
    """
    if not tweet['retweeted'] and not tweet['is_quote_status'] and not tweet['truncated']:
        if len(tweet['entities']['hashtags']) <= 3 and len(tweet['entities']['user_mentions']) <= 3 and len(
                tweet['entities']['urls']) <= 2:
            return True
    elif not tweet['retweeted'] and not tweet['is_quote_status']:
        if len(tweet['extended_tweet']['entities']['hashtags']) <= 3 and len(
                tweet['extended_tweet']['entities']['user_mentions']) <= 3 and \
                len(tweet['extended_tweet']['entities']['urls']) <= 2:
            return True


def change_columns(tweet):
    """
    :param tweet: json from twitter API

    Return dictionary with only few columns:
    - id - unique tweet id
    - init - tweet text
    - entities - entities in this tweet
    - created_at - time in which this tweet is created
    """
    if tweet['truncated']:
        text = tweet['extended_tweet']['full_text']
        entities = tweet['extended_tweet']['entities']
    else:
        text = tweet['text']
        entities = tweet['entities']

    try:
        text = text[:text.rindex('https://t.co/')]
    except ValueError:
        pass

    return {"tweet_id": tweet['id_str'], "init": text, "entities": entities, "created_at": tweet['created_at']}


def process_rdd(rdd, host=HOST_NAME_DATABASE, port=DATABASE_PORT, db=DATABASE_NAME,
                collection=INPUT_TWEETS_COLLECTION_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD,
                auth_db=DATABASE_AUTHDB):
    """
    :param rdd: rdd object which contain json string from Twitter API.
    :param host: mongodb host.
    :param port: mongodb port.
    :param db: database name..
    :param collection: collection name.
    :param user: user for authentication.
    :param password: password for authentication.
    :param auth_db: database for authentication.

    Process single partition of rdd and save into database.
    """
    connection = MongoClient(host, port,
                             username=user,
                             password=password,
                             authSource=auth_db,
                             authMechanism='SCRAM-SHA-256')
    try:
        for line in rdd:
            tweet = json.loads(line)
            if filter_tweets(tweet):
                document = change_columns(tweet)
                connection[db][collection].insert(document)
    except ValueError:
        pass


connection = MongoClient(HOST_NAME_DATABASE, DATABASE_PORT,
                         username=DATABASE_USER,
                         password=DATABASE_PASSWORD,
                         authSource=DATABASE_AUTHDB,
                         authMechanism='SCRAM-SHA-256')
if DATABASE_NAME not in connection.list_database_names():
    mongo_init(connection)

# create spark configuration
my_spark = SparkSession \
    .builder \
    .appName("TwitterStreamApp") \
    .getOrCreate()

my_spark.conf.set('spark.executor.pyspark.memory', '0.5g')

# create spark context with the above configuration
sc = my_spark.sparkContext
sc.setLogLevel("ERROR")
# create the Streaming Context from the above spark context with interval size 2 seconds
ssc = StreamingContext(sc, 15)
# setting a checkpoint to allow RDD recovery
ssc.checkpoint("checkpoint_TwitterStreamApp")
# read data from port 9009
dataStream = ssc.socketTextStream(HOST_NAME_TWITTER, TWITTER_PORT)
# do processing for each RDD generated in each interval
dataStream.foreachRDD(lambda rdd: rdd.foreachPartition(process_rdd))
# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
