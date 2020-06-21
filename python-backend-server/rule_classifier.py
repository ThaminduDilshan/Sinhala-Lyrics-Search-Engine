
writer_tokens = ['හදපු', 'භැදූ', 'භැදුව', 'ලියන', 'ලියන්න', 'ලියා', 'ලියූ', 'ලිව්ව', 'ලිව්', 'ලීව', 'ලියපු', 'ලියා ඇත', 'ලියා ඇති', 'රචිත', 'ලියන ලද']
artist_tokens = ['කියන', 'කියනා', 'කිව්ව', 'කිව්', 'කිව', 'කීව', 'කී', 'ගායනා කරන', 'ගයන', 'ගායනා', 'ගායනය', 'ගායනා කළා', 'ගායනා කල']
music_direc_tokens = ['අධ්‍යක්ෂණය', 'සංගීතමය', 'සංගීතවත්']
rating_tokens = ['ඉහල', 'ඉහළම', 'හොඳ', 'හොඳම', 'වැඩිපුර', 'වැඩිපුරම', 'ජනප්රිය', 'ජනප්රියම', 'ජනප්‍රිය', 'ජනප්‍රියම']
song_tokens = ['ගීත', 'සිංදු']


def classify(token_list):
    """
    Check given token list against rule based classifier to identify if the query is for an artist name, 
    lyric writer name, music director name or rating query

    Parameters:
    token_list (list): list of tokens/ words

    Returns:
    list (writer_q, artist_q, md_q, rate_q): If a song token present, False otherwise
    """

    writer_q = False
    artist_q = False
    md_q = False
    rate_q = False
    song_token = False
    
    for token in token_list:
        if token in writer_tokens:
            writer_q = True
        if token in artist_tokens:
            artist_q = True
        if token in music_direc_tokens:
            md_q = True
        if token in rating_tokens:
            rate_q = True
        if token in song_tokens:
            song_token = True

    if song_token:
        return (writer_q, artist_q, md_q, rate_q)
    return False


def is_rating_query(token_list):
    """
    Check given token list against rule based classifier to identify if the query is for a rating query

    Parameters:
    token_list (list): list of tokens/ words

    Returns:
    boolean: True if for a rating query, False otherwise
    """

    rate_q = False
    song_token = False

    for token in token_list:
        if token in rating_tokens:
            rate_q = True
        if token in song_tokens:
            song_token = True
    
    if song_token:
        return rate_q
    return False
