from typing import TypedDict, List
from pydantic import BaseModel, Field

class ResearchState(TypedDict):
    """
    State representation for the LangGraph multi-agent workflow.
    Tracks outputs across all stages of agent execution.
    """
    topic: str
    plan: str
    research_results: List[str]
    analysis: str
    final_report: str
    sources: List[dict]

class ResearchRequest(BaseModel):
    """
    Pydantic schema representing the POST /research request body.
    """
    topic: str = Field(
        ..., 
        description="The topic to be planned, researched, analyzed, and written about.",
        json_schema_extra={"example": "Artificial Intelligence"}
    )

class ResearchResponse(BaseModel):
    """
    Pydantic schema representing the POST /research response body.
    """
    topic: str = Field(
        ...,
        description="The topic that was researched."
    )
    report: str = Field(
        ...,
        description="The final compiled Markdown research report."
    )
    execution_status: str = Field(
        "completed",
        description="Execution status of the research workflow."
    )
    source_count: int = Field(
        0,
        description="Number of unique research sources referenced in the workflow."
    )
