import os
import time
import pickle

from delete_cluster import delete_clusters
from helpers.cluster_utils import search_clusters_of_vectors
from helpers.mongodb_worker import MongoDBWorker
from helpers.cluster_utils import save_clusters
from helpers.process_utils import collect_data_for_enriched, load_data_from_db
from helpers.process_utils import save_in_db_clusters_staff, save_in_db_tweets_score_and_cluster, save_word_score
from helpers.sent2vec_wrapper import Sent2VecWrapper
from helpers.spell_checker_wrapper import SpellCheckerWrapper

from requests import get

from smafed.enrichment import EnrichmentLayer
from smafed.ranker import Ranker
from smafed.semantic_histogram_clusterization import SemanticHistogramClusterization
from smafed.summarizer import Summarizer
from smafed.tweet_transformer import TweetTransformer

import nltk

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

DATABASE_NAME = os.getenv("DATABASE_NAME", "event_detection_db")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", '27017'))

INPUT_TWEETS_COLLECTION_NAME = os.getenv("INPUT_TWEETS_COLLECTION_NAME", "tweets_input")
IKB_COLLECTION_NAME = os.getenv("IKB_COLLECTION_NAME", "IKB")
PROCESSED_TWEETS_COLLECTION_NAME = os.getenv("PROCESSED_TWEETS_COLLECTION_NAME", "tweets_processed")
CLUSTER_COLLECTION_NAME = os.getenv("CLUSTER_COLLECTION_NAME", "cluster")
USED_SLANG_COLLECTION_NAME = os.getenv("USED_SLANG_COLLECTION_NAME", "used_slang")

URL_FOR_SENTTOVEC_MODEL = os.getenv("URL_FOR_SENTTOVEC_MODEL",
                                    "https://freefly19.ams3.digitaloceanspaces.com/smafed/torontobooks_unigrams.bin")
URL_FOR_SPELLCHECKER_MODEL = os.getenv("URL_FOR_SPELLCHECKER_MODEL",
                                       "https://freefly19.ams3.digitaloceanspaces.com/smafed/en.bin")
NUM_OF_TOKENS = int(os.getenv("NUM_OF_TOKENS", 5))
SHR_MIN = float(os.getenv("SHR_MIN", 0.9))
SHR_THRESHOLD = float(os.getenv("SHR_THRESHOLD", 0.25))
HISTOGRAM_RATIO_COEFFICIENT = float(os.getenv("HISTOGRAM_RATIO_COEFFICIENT", 1))

PATH = os.path.dirname(os.path.abspath(__file__))


def download_models(url, path):
    """
    :param url: url from which download model
    :param path: path to location where save model
    Download file.
    """
    r = get(url, stream=True)
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def pipeline():
    dbworker = MongoDBWorker(DATABASE_NAME, DATABASE_HOST, DATABASE_PORT)
    start_common = time.time()
    tweets_df = load_data_from_db(dbworker, INPUT_TWEETS_COLLECTION_NAME)
    if tweets_df.shape[0]:
        # Cleaning
        cleaner = TweetTransformer(tweets_df['init'], NUM_OF_TOKENS, tweets_df['entities'])
        cleaner.preprocess()

        array_of_dicts = collect_data_for_enriched(tweets_df, cleaner.sentences)
        if len(array_of_dicts) != 0:
            # Enrichment
            model = Sent2VecWrapper(os.path.join(PATH, "data_smafed", "sent2vec_model.bin"))
            spell_correction_model = SpellCheckerWrapper(os.path.join(PATH, "data_smafed", "spellcorrection_model.bin"))
            enrichment = EnrichmentLayer(model, dbworker, IKB_COLLECTION_NAME, PROCESSED_TWEETS_COLLECTION_NAME,
                                         USED_SLANG_COLLECTION_NAME, spell_correction_model, NUM_OF_TOKENS)
            dict_from_enriched = enrichment.tweets_enrichment(array_of_dicts)

            if dict_from_enriched != {}:
                # Vectorisation
                vectors = model.vectorize_sentences(dict_from_enriched.values())

                # Clusterisation
                clusterization = SemanticHistogramClusterization(os.path.join(PATH, "data_smafed", "cluster"),
                                                                 shr_min=SHR_MIN,
                                                                 shr_threshold=SHR_THRESHOLD,
                                                                 histogram_ratio_coefficient=HISTOGRAM_RATIO_COEFFICIENT)
                clusterization.clustering_elements(vectors)

                # Extract clusters number in relation with tweets
                clusters_sequence = search_clusters_of_vectors(clusterization.clusters, vectors)
                dict_tweet_cluster = dict(zip(dict_from_enriched.values(), clusters_sequence))

                # Ranking phase
                ranker = Ranker(dict_tweet_cluster, dbworker, PROCESSED_TWEETS_COLLECTION_NAME)
                ranker.ranking_cluster()

                # Summarize phase
                summarizer = Summarizer(dict_tweet_cluster, dbworker, PROCESSED_TWEETS_COLLECTION_NAME, ranker.grouped_tweets)
                summarizer.summarize_clusters()

                save_in_db_clusters_staff(dbworker, CLUSTER_COLLECTION_NAME, ranker.cluster_scores, "score")
                save_in_db_clusters_staff(dbworker, CLUSTER_COLLECTION_NAME, clusterization.clusters_creating_time,
                                          "cluster_creating_time")
                save_clusters(clusterization.clusters, clusterization.clusters_creating_time,
                              os.path.join(PATH, "data_smafed", "cluster"))
                save_in_db_tweets_score_and_cluster(dbworker, PROCESSED_TWEETS_COLLECTION_NAME, dict_from_enriched,
                                                    clusters_sequence, summarizer.grouped_tweets_with_scores)
                save_word_score(ranker.grouped_tweets, dbworker, CLUSTER_COLLECTION_NAME)
                finish_common = time.time()
                print(f"Common working time {finish_common - start_common}")


if not os.path.exists(os.path.join(PATH, "data_smafed")):
    os.mkdir(os.path.join(PATH, "data_smafed"))
if not os.path.exists(os.path.join(PATH, "data_smafed", "spellcorrection_model.bin")):
    download_models(URL_FOR_SPELLCHECKER_MODEL, os.path.join(PATH, "data_smafed", "spellcorrection_model.bin"))
if not os.path.exists(os.path.join(PATH, "data_smafed", "sent2vec_model.bin")):
    download_models(URL_FOR_SENTTOVEC_MODEL, os.path.join(PATH, "data_smafed", "sent2vec_model.bin"))

while True:
    try:
        delete_clusters()
    except FileNotFoundError:
        pass
    try:
        pipeline()
    except MemoryError:
        pass
