from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets."""
    try:
        results = tavily.search(query=query, max_results=5)
    except Exception as e:
        return f"Search failed: {str(e)}"

    result_list = results.get("results", [])
    if not result_list:
        return "No search results found for this query."

    out = []
    for r in result_list:
        out.append(
            f"Title: {r.get('title', 'N/A')}\n"
            f"URL: {r.get('url', 'N/A')}\n"
            f"Snippet: {r.get('content', '')[:300]}\n"
        )

    return "\n-----\n".join(out)


@tool
def scrape_tool(url: str) -> str:
    """Scrape and return clean text content for a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except Exception as e:
        return f"Could not scrape URL ({url}): {str(e)}"

    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        if not text:
            return f"No readable text content found at {url}"
        return text[:3000]
    except Exception as e:
        return f"Could not parse content from {url}: {str(e)}"