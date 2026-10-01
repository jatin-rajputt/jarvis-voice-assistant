"""
Music Library Module for Jarvis Assistant.
Maps known song titles to YouTube links and provides robust fallback YouTube searching.
"""

import webbrowser
import urllib.parse

music = {
    "tu jdo ana": "https://youtu.be/Z4bn7RR5Yv0?si=ASceLafwuNeb4gcM",
    "arjun": "https://youtu.be/PhpscSjTnsk?si=axSdSd1s3LlQ1YFl",
    "zor na koi": "https://youtu.be/D7udVpKY0f8?si=7vDwUVMMZlop1gu9",
    "punjabi hits": "https://youtu.be/uK4oTnLcIV4?si=hsrYM5kXrnlqsVce",
    "sidhu moose wala": "https://www.youtube.com/watch?v=LCRfUYv6gqU&list=RDLCRfUYv6gqU&start_radio=1",
    "karan aujla":"https://www.youtube.com/watch?v=W0--lTnDEgQ&list=RDW0--lTnDEgQ&start_radio=1"
}

def play_song(query):
    """
    Finds a song in the music library dictionary or searches YouTube directly.
    Returns (song_title, url_opened). Never crashes.
    """
    if not query:
        url = "https://www.youtube.com"
        try:
            webbrowser.open(url)
        except Exception:
            pass
        return "YouTube", url

    clean_query = str(query).strip().lower()
    
    # 1. Check exact or partial match in dictionary
    for song_name, url in music.items():
        if song_name in clean_query or clean_query in song_name:
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"[Music Browser Error] {e}")
            return song_name, url

    # 2. Fallback: Search and play directly on YouTube
    encoded_query = urllib.parse.quote(query.strip())
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    try:
        webbrowser.open(search_url)
    except Exception as e:
        print(f"[YouTube Search Browser Error] {e}")
    return query.strip(), search_url