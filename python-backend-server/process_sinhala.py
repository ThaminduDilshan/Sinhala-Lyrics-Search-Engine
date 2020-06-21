from sinling import SinhalaTokenizer
from packages.SinhalaStemming import sinhalaStemmer


def get_sn_process_setup():
    """
    Returns a tokenizer and stemmer object for sinhala language
    """

    tokenizer = SinhalaTokenizer()
    stemmer = sinhalaStemmer.stemmer()

    return tokenizer, stemmer


def token_stem(sentence, tokenizer, stemmer):
    """
    Tokenize a given sentence and returns the stemmer output

    Parameters:
    sentence (str): query string
    tokenizer (obj): Tokenizer object
    stemmer (obj): stemmer object

    Returns:
    list: processed token list
    str: processed query string
    """

    final_str = ''
    word_list = tokenizer.tokenize(sentence)
    stemmer.stemming(word_list)

    for word in word_list:
        final_str += word + ' '

    return word_list, final_str[:-1]
