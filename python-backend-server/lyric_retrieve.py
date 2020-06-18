import flask
from flask_cors import CORS, cross_origin
import json
from elasticsearch import Elasticsearch
from mtranslate import translate


es = Elasticsearch('localhost', port=9200)


def query_es_basic(search_term, limit):
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    res = es.search(
        index = 'sinhala_lyrics',
        size = limit,
        body = {
            'query': {
                'multi_match': {
                    'query': search_term,
                    'fields': [
                        "songName^4",
                        "artist^4",
                        "genre^2",
                        "lyricWriter^2",
                        "musicDirector^2",
                        # "key",
                        # "beat"
                    ]
                }
            }
        }
    )

    return res


def basicSearch(obj):
    language = obj['language']
    limit = obj['size']
    query = obj['query']

    if language == 'en':
        query = translate(query, 'si', 'en')

    return query_es_basic(query, limit)


# initialize flask app
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'tdj lyric app'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/basicsearch": {"origins": "http://localhost:4200"}})


@app.route('/basicsearch', methods=['POST'])
def serve():
    return flask.jsonify(basicSearch(flask.request.form))


if __name__ == '__main__':
     app.run(host='127.0.0.1', port='5002')
