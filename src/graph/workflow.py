import logging
from langgraph.graph import StateGraph, START, END
from src.models.schemas import ResearchState
from src.agents.planner import PlannerAgent
from src.agents.researcher import ResearchAgent
from src.agents.analyzer import AnalysisAgent
from src.agents.writer import WriterAgent

from src.llm.client_factory import get_llm_client

logger = logging.getLogger(__name__)

# Resolve pluggable LLM client singleton
llm_client = get_llm_client()

# Initialize agent singletons injecting the LLM client dependency
planner_agent = PlannerAgent(llm=llm_client)
research_agent = ResearchAgent(llm=llm_client)
analysis_agent = AnalysisAgent(llm=llm_client)
writer_agent = WriterAgent(llm=llm_client)

# Define state transition graph using our custom ResearchState
workflow = StateGraph(ResearchState)

# Register execution nodes
# Node functions take the current state and return state updates to merge
workflow.add_node("planner", lambda state: planner_agent.execute(state))
workflow.add_node("researcher", lambda state: research_agent.execute(state))
workflow.add_node("analyzer", lambda state: analysis_agent.execute(state))
workflow.add_node("writer", lambda state: writer_agent.execute(state))

# Construct workflow execution path: Start -> Planner -> Researcher -> Analyzer -> Writer -> End
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "analyzer")
workflow.add_edge("analyzer", "writer")
workflow.add_edge("writer", END)

# Compile graph into a runnable LangGraph Application
# This validates the graph connectivity and exposes invoke/ainvoke interfaces
app = workflow.compile()
logger.info("LangGraph workflow successfully compiled.")
