import logging
from src.core.config import settings
from src.llm.llm_interface import BaseLLMClient, MockLLMClient
from src.llm.openai_client import OpenAIClient

logger = logging.getLogger(__name__)

# Singleton client instance
_llm_client_instance: BaseLLMClient | None = None

def get_llm_client() -> BaseLLMClient:
    """
    Factory function to retrieve the active LLM client singleton.
    Provides a decoupled injection point to switch between mock and real OpenAI clients.
    """
    global _llm_client_instance
    if _llm_client_instance is None:
        # Check settings to toggle active LLM client.
        # To enable OpenAI, simply switch the condition or set a configuration flag.
        # Currently, we force MockLLMClient per instructions.
        use_mock = True
        
        if not use_mock and settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-xxxxxxxxxxxxxxxx":
            logger.info("Resolving real OpenAIClient connection.")
            _llm_client_instance = OpenAIClient()
        else:
            logger.info("Resolving MockLLMClient engine.")
            _llm_client_instance = MockLLMClient()
            
    return _llm_client_instance
