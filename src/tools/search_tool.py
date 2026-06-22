import logging
from typing import List, Dict
from tavily import TavilyClient
from src.core.config import settings

logger = logging.getLogger(__name__)

class TavilySearchTool:
    """
    Production-grade wrapper for the Tavily Search API.
    Retrieves web results and structures them consistently.
    """
    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize the Tavily Client using provided API key or environment settings.
        """
        self.api_key = api_key or settings.TAVILY_API_KEY
        if not self.api_key:
            logger.warning("Tavily API key is not set. TavilySearchTool may fail to execute queries.")
        
        try:
            self.client = TavilyClient(api_key=self.api_key) if self.api_key else None
        except Exception as exc:
            logger.error(f"Failed to instantiate TavilyClient: {exc}", exc_info=True)
            self.client = None

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Query Tavily Search API with timeout and error handling.
        
        Args:
            query (str): Search term.
            max_results (int): Maximum query results.
            
        Returns:
            List[Dict[str, str]]: Structured results containing title, url, and content.
        """
        logger.info(f"TavilySearchTool: Searching for query: '{query}' (limit: {max_results})")
        
        if not self.client:
            raise RuntimeError("TavilySearchTool: Client has not been initialized (check API key).")
        
        try:
            # Call Tavily API (TavilyClient wraps request calls internally)
            # We query search results.
            response = self.client.search(query=query, max_results=max_results)
            results = response.get("results", [])
            
            mapped_results = []
            for r in results:
                mapped_results.append({
                    "title": r.get("title") or "Untitled Source",
                    "url": r.get("url") or "No URL Provided",
                    "content": r.get("content") or "No content snippet available."
                })
            
            logger.info(f"TavilySearchTool: Successfully fetched {len(mapped_results)} records.")
            return mapped_results
            
        except Exception as exc:
            logger.error(f"TavilySearchTool: Exception raised searching for '{query}': {exc}", exc_info=True)
            raise RuntimeError(f"Tavily search request failed: {str(exc)}") from exc
