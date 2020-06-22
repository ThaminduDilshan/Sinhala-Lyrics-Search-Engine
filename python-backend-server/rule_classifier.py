
writer_tokens = ['හදපු', 'භැදූ', 'භැදුව', 'ලියන', 'ලියන්න', 'ලියා', 'ලියූ', 'ලිව්ව', 'ලිව්', 'ලීව', 'ලියපු', 'ලියා ඇත', 'ලියා ඇති', 'රචිත', 'ලියන ලද', 'ලිඛිත', 'පදරචනය']
artist_tokens = ['කියන', 'කියනා', 'කිව්ව', 'කිව්', 'කිව', 'කීව', 'කී', 'ගායනා කරන', 'ගයන', 'ගායනා', 'ගායනය', 'ගායනා කළා', 'ගායනා කල']
music_direc_tokens = ['අධ්‍යක්ෂණය', 'සංගීතමය', 'සංගීතවත්']
rating_tokens = ['ඉහල', 'ඉහළම', 'හොඳ', 'හොඳම', 'වැඩිපුර', 'වැඩිපුරම', 'ජනප්රිය', 'ජනප්රියම', 'ජනප්‍රිය', 'ජනප්‍රියම', 'ප්‍රකට', 'ප්‍රසිද්ධ']
song_tokens = ['ගීත', 'සිංදු', 'සින්දු']


def classify(token_list):
    """
    Check given token list against rule based classifier to identify if the query is for an artist name, 
    lyric writer name, music director name or rating query

    Parameters:
    token_list (list): list of tokens/ words

    Returns:
    list (writer_q, artist_q, md_q, rate_q, cleaned_query_string): If a song token present, False otherwise
    """

    writer_q = False
    artist_q = False
    md_q = False
    rate_q = False
    song_token = False
    other_tokens_str = ''
    
    for token in token_list:
        if token in writer_tokens:
            writer_q = True
        elif token in artist_tokens:
            artist_q = True
        elif token in music_direc_tokens:
            md_q = True
        elif token in rating_tokens:
            rate_q = True
        elif token in song_tokens:
            song_token = True
        else:
            other_tokens_str += token + ' '

    if song_token:
        return (writer_q, artist_q, md_q, rate_q, other_tokens_str[:-1])
    return False


def is_rating_query(token_list):
    """
    Check given token list against rule based classifier to identify if the query is for a rating query

    Parameters:
    token_list (list): list of tokens/ words

    Returns:
    list (rate_q, cleaned_query_string): If token_list for a rating query, False otherwise
    """

    rate_q = False
    song_token = False
    other_tokens_str = ''

    for token in token_list:
        if token in rating_tokens:
            rate_q = True
        elif token in song_tokens:
            song_token = True
        else:
            other_tokens_str += token + ' '
    
    if song_token:
        return rate_q, other_tokens_str[:-1]
    return False, False
