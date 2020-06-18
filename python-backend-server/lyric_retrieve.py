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
                        "lyric^4",
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


def query_es_adv(search_term, artist, lyric_writer, music_by, genre, key, beat, limit):
    must_list = []
    should_list = []
    
    if search_term != '':
        should_list.append({'match': {'songName': search_term}})
        should_list.append({'match': {'lyric': search_term}})
        should_list.append({'match': {'artist': search_term}})
        should_list.append({'match': {'lyricWriter': search_term}})

    if artist != '':
        must_list.append({'match': {'artist': artist}})
    if lyric_writer != '':
        must_list.append({'match': {'lyricWriter': lyric_writer}})
    if music_by != '':
        must_list.append({'match': {'musicDirector': music_by}})
    if genre != '':
        must_list.append({'match': {'genre': genre}})
    if key != '':
        must_list.append({'match': {'key': key}})
    if beat != '':
        must_list.append({'match': {'beat': beat}})
    
    res = es.search(
        index = 'sinhala_lyrics',
        size = limit,
        body = {
            'query': {
                'bool': {
                    'must': must_list,
                    'should': should_list
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


def advancedSearch(obj):
    language = obj['language']
    limit = obj['size']

    query = obj['query']
    artist = obj['artist']
    lyric_writer = obj['lyric_writer']
    music_by = obj['music_by']
    genre = obj['genre']
    key = obj['key']
    beat = obj['beat']

    if language == 'en':
        if query != '':
            query = translate(query, 'si', 'en')
        if artist != '':
            artist = translate(artist, 'si', 'en')
        if lyric_writer != '':
            lyric_writer = translate(lyric_writer, 'si', 'en')
        if music_by != '':
            music_by = translate(music_by, 'si', 'en')
        if genre != '':
            genre = translate(genre, 'si', 'en')

    return query_es_adv(query, artist, lyric_writer, music_by, genre, key, beat, limit)


# initialize flask app
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'tdj lyric app'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

@app.route('/basicsearch', methods=['POST'])
def serve():
    return flask.jsonify(basicSearch(flask.request.form))

@app.route('/advancedsearch', methods=['POST'])
def serve2():
    return flask.jsonify(advancedSearch(flask.request.form))


if __name__ == '__main__':
     app.run(host='127.0.0.1', port='5002')
