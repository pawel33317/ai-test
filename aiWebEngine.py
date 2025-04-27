import aiConfig, aiDebug
import requests
from bs4 import BeautifulSoup
try:
    from googlesearch import search as google_search
except ImportError:
    raise ImportError("Install packet 'googlesearch-python' or 'beautifulsoup4'.")

# Helper functions
def find_helpful_urls(query):
    """Perform a web search and return a list of URLs."""
    query = query + " wiki"
    aiDebug.debug_print(f"--- WEB SEARCH ---\n   Search query: {query.replace('\n', ' ')}")
    try:
        return list(google_search(query, num_results=aiConfig.WEB_SEARCH_PAGES))
    except Exception as e:
        aiDebug.debug_print(f"   Error during web search: {e[0:120]}")
        return []

def get_url_content(url):
    """Fetch and return plain text content from a URL."""
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        aiDebug.debug_print(f"   Error fetching content from {url}: {e}")
        return None