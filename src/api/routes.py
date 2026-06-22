import logging
from fastapi import APIRouter, BackgroundTasks
from src.models.schemas import ResearchRequest, ResearchResponse
from src.graph.workflow import app as workflow_app

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

@router.post("/research", response_model=ResearchResponse)
async def research_endpoint(request: ResearchRequest) -> ResearchResponse:
    """
    Receives research topic, executes the agent workflow synchronously,
    and returns the compiled report with completion status.
    """
    logger.info(f"POST /research endpoint invoked for topic: '{request.topic}'")
    
    initial_state = {
        "topic": request.topic,
        "plan": "",
        "research_results": [],
        "analysis": "",
        "final_report": "",
        "sources": []
    }
    
    try:
        # Run graph workflow using asynchronous invocation interface, blocking until complete
        result = await workflow_app.ainvoke(initial_state)
        logger.info(f"Workflow execution completed for topic: '{request.topic}'")
        
        sources_list = result.get("sources", [])
        
        return ResearchResponse(
            topic=request.topic,
            report=result.get("final_report", ""),
            execution_status="completed",
            source_count=len(sources_list)
        )
    except Exception as exc:
        logger.error(f"Error during workflow run for '{request.topic}': {exc}", exc_info=True)
        # Raise HTTP exception or handle error state
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500, 
            detail=f"Workflow failed to complete for topic '{request.topic}': {str(exc)}"
        )
