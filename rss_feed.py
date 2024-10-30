# rss_feed.py
import feedparser

def fetch_rss_feed(url, limit=5):
    """
    Fetches and parses an RSS feed from the specified URL.

    Args:
        url (str): The URL of the RSS feed.
        limit (int): The maximum number of entries to return.

    Returns:
        list: A list of dictionaries containing title, link, and published date for each entry.
    """
    feed = feedparser.parse(url)
    entries = []

    for entry in feed.entries[:limit]:  # Limit to the specified number of entries
        entries.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.get('published', 'No date available')
        })

    return entries

