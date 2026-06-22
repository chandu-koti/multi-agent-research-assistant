import logging
import json
from src.models.schemas import ResearchState
from src.llm.llm_interface import BaseLLMClient

from src.tools.search_tool import TavilySearchTool

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Agent responsible for taking the planner's questions and executing live web searches via Tavily.
    """
    def __init__(self, llm: BaseLLMClient) -> None:
        """
        Initialize ResearchAgent injecting LLM interface client and Tavily Search Tool.
        """
        self.llm = llm
        self.search_tool = TavilySearchTool()
        logger.info("ResearchAgent initialized and bound to TavilySearchTool.")

    def execute(self, state: ResearchState) -> dict:
        """
        Query Tavily for each question, collect and deduplicate sources, and update state.
        
        Args:
            state (ResearchState): Current workflow state containing 'plan'.
            
        Returns:
            dict: Updated key-value pairs ('research_results' and 'sources').
        """
        topic = state.get("topic")
        plan_str = state.get("plan", "{}")
        
        logger.info(f"ResearchAgent starting research execution flow for topic: '{topic}'")
        
        try:
            plan_dict = json.loads(plan_str)
        except json.JSONDecodeError as exc:
            logger.error(f"ResearchAgent failed to parse research plan JSON: {exc}.", exc_info=True)
            plan_dict = {}

        questions = plan_dict.get("research_questions", [])
        if not questions:
            logger.warning("No research questions found in plan state. Using topic query fallback.")
            questions = [f"{topic} research overview"]

        findings = []
        sources = []
        seen_urls = set()

        try:
            for query in questions:
                logger.debug(f"ResearchAgent: Dispatching query to Tavily: '{query}'")
                try:
                    search_results = self.search_tool.search(query, max_results=3)
                    for res in search_results:
                        url = res.get("url")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            findings.append(res.get("content", ""))
                            sources.append({
                                "title": res.get("title") or "Untitled Source",
                                "url": url
                            })
                except Exception as query_exc:
                    # Reraise exception to invoke general search failure flow
                    logger.warning(f"ResearchAgent query failed: {query_exc}. Reraising for handler.")
                    raise query_exc
            
            # If search completed but returned no results
            if not findings:
                logger.warning("Tavily searches returned empty results. Invoking fallback.")
                findings = [f"No online research details discovered for {topic}."]
                sources = []

        except Exception as exc:
            logger.error(
                f"ResearchAgent: Tavily query execution failed: {exc}. Initializing fallback content.",
                exc_info=True
            )
            # Gracefully update results with failure message without throwing error to main thread
            findings = ["Tavily search failed. Using fallback system content."]
            sources = []

        logger.info(f"ResearchAgent finished: Gathered {len(findings)} unique snippets from {len(sources)} sources.")
        return {
            "research_results": findings,
            "sources": sources
        }
