import logging
from src.models.schemas import ResearchState
from src.llm.llm_interface import BaseLLMClient

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Agent responsible for analyzing gathered research notes to produce findings, opportunities, and risks.
    Consumes a pluggable LLM interface to support decoupled OpenAI integration.
    """
    def __init__(self, llm: BaseLLMClient) -> None:
        """
        Initialize AnalysisAgent with a designated LLM client.
        """
        self.llm = llm
        logger.info("AnalysisAgent successfully initialized with LLM client.")

    def execute(self, state: ResearchState) -> dict:
        """
        Execute analysis processing over research findings.
        
        Args:
            state (ResearchState): Current workflow state containing 'research_results'.
            
        Returns:
            dict: Updated key-value pairs (the structured string 'analysis').
        """
        topic = state.get("topic")
        research_results = state.get("research_results", [])
        
        logger.info(f"AnalysisAgent analyzing {len(research_results)} notes for topic: '{topic}'")
        
        # Invoke LLM client interface to generate synthesized analysis
        analysis_str = self.llm.generate_analysis(topic, research_results)
        
        logger.info("AnalysisAgent analysis generation complete.")
        return {"analysis": analysis_str}
