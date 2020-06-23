import flask
from flask_cors import CORS, cross_origin
import json
from elasticsearch import Elasticsearch
from mtranslate import translate
import re
import process_sinhala
from rule_classifier import classify, is_rating_query


index_name = 'sinhala_lyrics_tokenized'
es = Elasticsearch('localhost', port=9200)
tokenizer = None
stemmer = None
beat_pattern = re.compile('\d*\/\d*')


def query_es_basic(search_term, limit):
    """
    Query ElasticSearch for a basic search query.
    Uses multi-match query.
    Note that certain fields are boosted (^).
    """

    num_list = [int(s) for s in search_term.split() if s.isdigit()]
    if len(num_list) != 0 and not beat_pattern.search(search_term):
        limit = num_list[0]
    
    res = es.search(
        index = index_name,
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
            },
            "aggs": {
                "artist_filter": {
                    "terms": {
                        "field": "artist.keyword",
                        "size": 5
                    }
                },
                "lyric_filter": {
                    "terms": {
                        "field": "lyricWriter.keyword",
                        "size": 5
                    }
                },
                "genre_filter": {
                    "terms": {
                        "field": "genre.keyword",
                        "size": 5
                    }
                }
            }
        }
    )

    return res


def query_es_adv(search_term, artist, lyric_writer, music_by, genre, key, beat, limit, is_ranking=False):
    """
    Query ElasticSearch for an advanced search query.
    Uses bool query.
    """

    must_list = []
    should_list = []
    aggs_dict = {}

    num_list = [int(s) for s in search_term.split() if s.isdigit()]
    if len(num_list) != 0 and not beat_pattern.search(search_term):
        limit = num_list[0]
    
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

    if artist != '' and lyric_writer == '':
        aggs_dict['lyric_filter'] = {'terms': {'field': 'lyricWriter.keyword', 'size': 5}}
    if artist != '' and genre == '':
        aggs_dict['genre_filter'] = {'terms': {'field': 'genre.keyword', 'size': 5}}
    
    if lyric_writer != '' and artist == '':
        aggs_dict['artist_filter'] = {'terms': {'field': 'artist.keyword', 'size': 5}}
    if lyric_writer != '' and genre == '':
        aggs_dict['genre_filter'] = {'terms': {'field': 'genre.keyword', 'size': 5}}
    
    if genre != '' and lyric_writer == '':
        aggs_dict['lyric_filter'] = {'terms': {'field': 'lyricWriter.keyword', 'size': 5}}
    if genre != '' and artist == '':
        aggs_dict['artist_filter'] = {'terms': {'field': 'artist.keyword', 'size': 5}}

    if is_ranking:
        res = es.search(
            index = index_name,
            size = limit,
            body = {
                'query': {
                    'bool': {
                        'must': must_list,
                        'should': should_list
                    }
                },
                'sort': [
                    {
                        'views': {
                            'order': 'desc'
                        }
                    }
                ],
                'aggs': aggs_dict
            }
        )
    
    else:
        res = es.search(
            index = index_name,
            size = limit,
            body = {
                'query': {
                    'bool': {
                        'must': must_list,
                        'should': should_list
                    }
                },
                'aggs': aggs_dict
            }
        )

    return res


def query_es_basic_boosted(search_term, limit, classify_out):
    """
    Query ElasticSearch for a basic search query with classifier results.
    Uses bool query.
    """

    should_list = []
    aggs_dict = {}

    num_list = [int(s) for s in search_term.split() if s.isdigit()]
    if len(num_list) != 0 and not beat_pattern.search(search_term):
        limit = num_list[0]

    if classify_out[0]:       # lyric writer
        should_list.append({'match': {'lyricWriter': classify_out[4]}})
    elif classify_out[1]:       # artist
        should_list.append({'match': {'artist': classify_out[4]}})
    elif classify_out[2]:       # music director
        should_list.append({'match': {'musicDirector': classify_out[4]}})
    else:
        should_list.append({'match': {'songName': classify_out[4]}})
        should_list.append({'match': {'lyric': classify_out[4]}})
        should_list.append({'match': {'artist': classify_out[4]}})
    
    if classify_out[0] and not classify_out[1]:     # lyric writer and not artist
        aggs_dict['artist_filter'] = {'terms': {'field': 'artist.keyword', 'size': 5}}
    if classify_out[1] and not classify_out[0]:     # artist and not lyric writer
        aggs_dict['lyric_filter'] = {'terms': {'field': 'lyricWriter.keyword', 'size': 5}}
    aggs_dict['genre_filter'] = {'terms': {'field': 'genre.keyword', 'size': 5}}

    if classify_out[3]:         # if rating query
        res = es.search(
            index = index_name,
            size = limit,
            body = {
                'query': {
                    'bool': {
                        'should': should_list
                    }
                },
                'sort': [
                    {
                        'views': {
                            'order': 'desc'
                        }
                    }
                ],
                'aggs': aggs_dict
            }
        )
    
    else:
        res = es.search(
            index = index_name,
            size = limit,
            body = {
                'query': {
                    'bool': {
                        'should': should_list
                    }
                },
                'aggs': aggs_dict
            }
        )

    return res


def basicSearch(obj):
    """
    Function to perform a basic search query with frontend return objects
    """

    language = obj['language']
    limit = obj['size']
    query = obj['query']

    if language == 'en':
        query = translate(query, 'si', 'en')

    # get token list
    token_list, query = process_sinhala.token_stem(query, tokenizer, stemmer)
    rules = classify(token_list)

    if not rules:           # not classified
        print('[DEBUG] Not rating query => query_es_basic')
        return query_es_basic(query, limit)
    else:
        print('[DEBUG] Rating query => query_es_basic_boosted')
        return query_es_basic_boosted(query, limit, rules)


def advancedSearch(obj):
    """
    Function to perform an advanced search query with frontend return objects
    """

    language = obj['language']
    limit = obj['size']

    query = obj['query']
    artist = obj['artist']
    lyric_writer = obj['lyric_writer']
    music_by = obj['music_by']
    genre = obj['genre']
    key = obj['key']
    beat = obj['beat']

    # if language is english, translate to sinhala
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

    # get token list
    token_list, query = process_sinhala.token_stem(query, tokenizer, stemmer)

    # check whether a rating query
    is_rating, token_query = is_rating_query(token_list)

    if(is_rating):
        query = token_query
        print('[DEBUG] Rating query => query_es_adv')
        return query_es_adv(query, artist, lyric_writer, music_by, genre, key, beat, limit, True)
    else:
        print('[DEBUG] Not rating query => query_es_adv')
        return query_es_adv(query, artist, lyric_writer, music_by, genre, key, beat, limit, False)


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
    tokenizer, stemmer = process_sinhala.get_sn_process_setup()

    app.run(host='127.0.0.1', port='5002')
