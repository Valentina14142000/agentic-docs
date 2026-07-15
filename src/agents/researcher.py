import re
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def web_search(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Search the web using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                }
                for r in results
            ]
    except Exception as e:
        print(f"Search failed for query '{query}': {e}")
        return []

def scrape_webpage(url: str, max_chars: int = 4000) -> str:
    """Fetches a webpage, cleans the HTML, and returns the core text body."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching webpage: {str(e)}"

    soup = BeautifulSoup(response.text, "html.parser")

    # Decompose boilerplates
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        element.decompose()

    text = soup.get_text(separator="\n")
    clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
    sanitized_text = "\n".join(clean_lines)

    if len(sanitized_text) > max_chars:
        return sanitized_text[:max_chars] + "\n\n[Content truncated for length]..."
        
    return sanitized_text
