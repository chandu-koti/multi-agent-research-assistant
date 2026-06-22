import logging
import json
from src.models.schemas import ResearchState
from src.llm.llm_interface import BaseLLMClient

logger = logging.getLogger(__name__)

class WriterAgent:
    """
    Agent responsible for structuring the final research report in Markdown.
    Consumes a pluggable LLM interface to support decoupled OpenAI integration.
    """
    def __init__(self, llm: BaseLLMClient) -> None:
        """
        Initialize WriterAgent with a designated LLM client.
        """
        self.llm = llm
        logger.info("WriterAgent successfully initialized with LLM client.")

    def execute(self, state: ResearchState) -> dict:
        """
        Execute report formulation and assembly.
        
        Args:
            state (ResearchState): Current workflow state containing plan, research_results, and analysis.
            
        Returns:
            dict: Updated key-value pairs (the markdown string 'final_report').
        """
        topic = state.get("topic")
        plan_str = state.get("plan", "{}")
        research_results = state.get("research_results", [])
        analysis = state.get("analysis", "")
        sources = state.get("sources", [])
        
        logger.info(f"WriterAgent compiling report for topic: '{topic}'")
        
        try:
            plan_dict = json.loads(plan_str)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse research plan JSON during writing phase: {exc}", exc_info=True)
            plan_dict = {}

        # Invoke LLM client interface to compile the complete markdown report with sources
        final_report = self.llm.generate_report(topic, plan_dict, research_results, analysis, sources)
        
        logger.info("WriterAgent report drafting completed.")
        return {"final_report": final_report}
