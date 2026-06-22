import logging
import json
from src.models.schemas import ResearchState
from src.llm.llm_interface import BaseLLMClient

logger = logging.getLogger(__name__)

class PlannerAgent:
    """
    Agent responsible for analyzing the research topic and creating a structured plan.
    Consumes a pluggable LLM interface to support decoupled OpenAI integration.
    """
    def __init__(self, llm: BaseLLMClient) -> None:
        """
        Initialize PlannerAgent with a designated LLM client.
        """
        self.llm = llm
        logger.info("PlannerAgent successfully initialized with LLM client.")

    def execute(self, state: ResearchState) -> dict:
        """
        Execute the planning phase using the LLM interface.
        
        Args:
            state (ResearchState): The current workflow state.
            
        Returns:
            dict: Updated key-value pairs (the JSON-serialized 'plan').
        """
        topic = state.get("topic")
        logger.info(f"PlannerAgent formulating plan for topic: '{topic}'")
        
        # Invoke LLM client interface to generate plan dict
        plan_dict = self.llm.generate_plan(topic)
        
        # Serialize the dictionary to a string to conform to state schema
        plan_json_str = json.dumps(plan_dict, indent=2)
        
        logger.info("PlannerAgent plan generated and saved.")
        return {"plan": plan_json_str}
