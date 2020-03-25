import json
import os
import pymongo
import re
from collections import Iterable
from tempfile import TemporaryFile

from bson import ObjectId
from cachetools import cached, TTLCache
from flask import Flask, jsonify, request, send_file
from flask_pymongo import PyMongo
from wordcloud import WordCloud

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', '27017')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'event_detection_db')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')
MONGO_USER= os.getenv('MONGO_USER', '')
MONGO_AUTHDB= os.getenv('MONGO_AUTHDB', '')

app = Flask(__name__)
if MONGO_USER == "":
    app.config["MONGO_URI"] = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}"
else:
    app.config["MONGO_URI"] = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource={MONGO_AUTHDB}"
mongo = PyMongo(app)


def enrich_slang_item_with_definition(slang):
    for dictionary_title in slang['payload']:
        for dictionary_item in slang['payload'][dictionary_title]:
            for d in dictionary_item['definition']:
                if len(d) > 0:
                    slang['description'] = d
                    slang['descriptionFrom'] = dictionary_title
                    return


def form_page_dto(content, page_number, page_size, total_items):
    total_pages = total_items // page_size + (1 if total_items % page_size > 0 else 0)

    return {
        'content': content,
        'size': page_size,
        'number': page_number,
        'totalPages': total_pages,
        'total': total_items,
        'first': page_number == 0,
        'last': page_number >= total_pages - 1
    }


def replace_mongo_object_id(a):
    if isinstance(a, Iterable) and not isinstance(a, dict):
        for el in a:
            el['_id'] = str(el['_id'])
    else:
        a['_id'] = str(a['_id'])


@cached(cache=TTLCache(maxsize=128, ttl=600))
def generate_word_cloud_image(words_as_json):
    words = json.loads(words_as_json)
    word_cloud = WordCloud(mode='RGBA',
                           background_color=None,
                           max_words=10,
                           prefer_horizontal=1,
                           colormap='tab10',
                           min_font_size=8)
    image = word_cloud.generate_from_frequencies(words).to_image()
    return image


def serve_pil_image(pil_img):
    f = TemporaryFile()
    pil_img.save(f, 'PNG', quality=100)
    f.seek(0)
    return send_file(f, mimetype='image/png')


@app.route('/api/used-slangs')
def used_slang_list():
    page = int(request.args.get('page', '0'))
    size = int(request.args.get('size', '10'))
    search = request.args.get('search', None)

    query = {}
    if search is not None:
        query['word'] = {'$regex': re.escape(search), '$options': 'i'}

    # TODO: Should be a "flag", which indicates that slangs have been used in some tweets
    slangs = list(mongo.db.used_slang.find(query, skip=page * size, limit=size))
    total_items = mongo.db.used_slang.count(query)

    replace_mongo_object_id(slangs)

    return jsonify(form_page_dto(slangs, page, size, total_items))


@app.route('/api/used-slangs/<used_slang_id>')
def used_slang_by_id(used_slang_id):
    used_slang = mongo.db.used_slang.find_one({'_id': ObjectId(used_slang_id)})
    replace_mongo_object_id(used_slang)
    used_slang['ikb'] = mongo.db.IKB.find_one({'_id': used_slang['ikb_id']})
    replace_mongo_object_id(used_slang['ikb'])

    return jsonify(used_slang)

@app.route('/api/events')
def event_list():
    page = int(request.args.get('page', '0'))
    size = int(request.args.get('size', '10'))

    events = list(mongo.db.cluster.find({}, skip=page * size, limit=size).sort([('score', pymongo.DESCENDING)]))
    replace_mongo_object_id(events)

    for event in events:
        event['tweets'] = list(mongo.db.tweets_processed.find({'cluster': event['cluster']}, limit=3).sort([('score', pymongo.DESCENDING)]))
        event['amount_of_tweets'] = mongo.db.tweets_processed.count({'cluster': event['cluster']})
        replace_mongo_object_id(event['tweets'])
        for tweet in event['tweets']:
            tweet['used_slang_ids'] = [str(id) for id in tweet['used_slang_ids']]

    total_items = mongo.db.cluster.count({})

    return jsonify(form_page_dto(events, page, size, total_items))


@app.route('/api/events/<cluster>')
def event_by_cluster_id(cluster):
    event_obj = mongo.db.cluster.find_one({'cluster': int(cluster)})
    replace_mongo_object_id(event_obj)
    event_obj['words'] = list(sorted(map(lambda word: {'word': word, 'score': event_obj['words'][word]}, event_obj['words']), key=lambda kv: kv['score'], reverse=True))

    return jsonify(event_obj)


@app.route('/api/events/<cluster>/tweets')
def tweets_by_cluster_id(cluster):
    page = int(request.args.get('page', '0'))
    size = int(request.args.get('size', '10'))

    tweets = list(mongo.db.tweets_processed.find({'cluster': int(cluster)}, skip=page * size, limit=size).sort([('score', pymongo.DESCENDING)]))
    total_items = mongo.db.tweets_processed.count({'cluster': int(cluster)})
    replace_mongo_object_id(tweets)

    for tweet in tweets:
        tweet['used_slang_ids'] = [str(id) for id in tweet['used_slang_ids']]

    return jsonify(form_page_dto(tweets, page, size, total_items))


@app.route('/api/events/<cluster>-cloud.png')
def event_word_cloud_by_id(cluster):
    event_cluster = mongo.db.cluster.find_one({'cluster': int(cluster)})

    image = generate_word_cloud_image(json.dumps(event_cluster['words']))
    return serve_pil_image(image)



if __name__ == '__main__':
    app.run(debug=True)
