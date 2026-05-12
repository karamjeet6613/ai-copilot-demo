from langchain_classic.tools import Tool
from tavily import TavilyClient
import os

def web_search(query: str) -> str:
    """Search the web and return top 3 results as text."""
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query, max_results=3)
        results = response.get("results", [])
        if not results:
            return "No results found."
        return "\n\n".join(
            f"**{r['title']}**\n{r['content']}\nSource: {r['url']}"
            for r in results
        )
    except Exception as e:
        return f"Search failed: {str(e)}"

search_tool = Tool(
    name="WebSearch",
    func=web_search,
    description="Search the internet for current information. Input: a search query string."
)
