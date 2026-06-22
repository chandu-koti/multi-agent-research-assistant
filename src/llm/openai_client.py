import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from src.core.config import settings
from src.llm.llm_interface import BaseLLMClient

logger = logging.getLogger(__name__)

# Pydantic schemas for LLM structured output parsing
class ResearchPlanSchema(BaseModel):
    topic: str = Field(..., description="The research topic.")
    research_questions: List[str] = Field(..., description="Key questions to investigate.")
    research_plan: List[str] = Field(..., description="Key steps in the research timeline.")

class ResearchNotesSchema(BaseModel):
    notes: List[str] = Field(..., description="List of detailed research notes.")


# Singleton ChatOpenAI instance placeholder
_chat_model: ChatOpenAI | None = None

def get_chat_model() -> ChatOpenAI:
    """
    Singleton resolver for ChatOpenAI. Sets up retry logic, models, and logging.
    """
    global _chat_model
    if _chat_model is None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY environment variable is not defined.")
            
        # Environment-driven model selection, retry handling, and configuration
        _chat_model = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
            max_retries=3,  # Native LangChain retry mechanism for rate-limits/transient errors
        )
        logger.info(f"Initialized ChatOpenAI singleton instance with model: {settings.OPENAI_MODEL}")
        
    return _chat_model


class OpenAIClient(BaseLLMClient):
    """
    Real OpenAI-powered client implementing BaseLLMClient.
    Provides structured prompts and invokes ChatOpenAI with structured schemas.
    """
    def __init__(self) -> None:
        try:
            self.model = get_chat_model()
        except Exception as exc:
            logger.error(f"Error during OpenAI model initialization: {exc}", exc_info=True)
            raise RuntimeError("Failed to configure OpenAI client model.") from exc

    def generate_plan(self, topic: str) -> Dict[str, Any]:
        logger.info(f"OpenAIClient generating structured plan for topic: '{topic}'")
        try:
            structured_model = self.model.with_structured_output(ResearchPlanSchema)
            prompt = (
                f"You are a Research Director. Generate a research plan for the topic: '{topic}'.\n"
                "Formulate critical questions and research milestones."
            )
            result = structured_model.invoke(prompt)
            # return model dict
            return result.model_dump()
        except Exception as exc:
            logger.error(f"Failed to generate plan via OpenAI: {exc}", exc_info=True)
            raise RuntimeError(f"OpenAI generate_plan execution failed: {exc}") from exc

    def generate_research_notes(self, topic: str, plan: Dict[str, Any]) -> List[str]:
        questions = plan.get("research_questions", [])
        logger.info(f"OpenAIClient generating research notes for topic: '{topic}' with {len(questions)} questions")
        try:
            structured_model = self.model.with_structured_output(ResearchNotesSchema)
            questions_str = "\n".join([f"- {q}" for q in questions])
            prompt = (
                f"You are an expert researcher investigating the topic: '{topic}'.\n"
                f"Conduct deep-dive research answering the following questions:\n{questions_str}\n\n"
                "Return a list of detailed, fact-filled research notes answering these questions."
            )
            result = structured_model.invoke(prompt)
            return result.notes
        except Exception as exc:
            logger.error(f"Failed to generate research notes via OpenAI: {exc}", exc_info=True)
            raise RuntimeError(f"OpenAI generate_research_notes execution failed: {exc}") from exc

    def generate_analysis(self, topic: str, research_results: List[str]) -> str:
        logger.info(f"OpenAIClient starting analysis of {len(research_results)} notes for topic: '{topic}'")
        try:
            notes_str = "\n\n".join(research_results)
            prompt = (
                f"You are a Senior Systems Analyst studying topic: '{topic}'.\n"
                f"Review the following research inputs:\n{notes_str}\n\n"
                "Synthesize and group your findings. You MUST structure the response EXACTLY using the following markdown headers:\n"
                "### KEY FINDINGS\n"
                "### OPPORTUNITIES\n"
                "### RISKS\n"
                "### FUTURE TRENDS\n"
            )
            result = self.model.invoke(prompt)
            return result.content
        except Exception as exc:
            logger.error(f"Failed to generate analysis via OpenAI: {exc}", exc_info=True)
            raise RuntimeError(f"OpenAI generate_analysis execution failed: {exc}") from exc

    def generate_report(
        self, topic: str, plan: Dict[str, Any], research_results: List[str], analysis: str, sources: List[Dict[str, str]]
    ) -> str:
        logger.info(f"OpenAIClient synthesizing final report for topic: '{topic}'")
        try:
            questions_str = "\n".join([f"- {q}" for q in plan.get("research_questions", [])])
            results_str = "\n\n".join(research_results)
            
            # Format sources for prompt injection
            sources_list = []
            for src in sources:
                title = src.get("title") or "Untitled Source"
                url = src.get("url") or "#"
                sources_list.append(f"- [{title}]({url})")
            sources_str = "\n".join(sources_list) if sources_list else "*No sources referenced.*"
            
            prompt = (
                f"You are a Professional Technical Writer. Draft a comprehensive report on '{topic}'.\n\n"
                f"Research Questions:\n{questions_str}\n\n"
                f"Research notes:\n{results_str}\n\n"
                f"Synthesized Analysis:\n{analysis}\n\n"
                f"Sources Reference:\n{sources_str}\n\n"
                "Compile this data into a professional markdown document. You MUST follow this exact structure:\n"
                "# Executive Summary\n"
                "# Research Questions\n"
                "# Key Findings\n"
                "# Opportunities\n"
                "# Risks\n"
                "# Future Trends\n"
                "# Sources\n"
                "# Conclusion\n"
            )
            result = self.model.invoke(prompt)
            return result.content
        except Exception as exc:
            logger.error(f"Failed to generate report via OpenAI: {exc}", exc_info=True)
            raise RuntimeError(f"OpenAI generate_report execution failed: {exc}") from exc
