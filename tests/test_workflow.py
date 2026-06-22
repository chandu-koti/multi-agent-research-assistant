from src.graph.workflow import app as workflow_app

def test_workflow_execution() -> None:
    """
    Verify that the compiled LangGraph workflow compiles, routes, and executes
    through all four agents, returning a complete state payload.
    """
    topic_query = "Distributed Databases"
    initial_state = {
        "topic": topic_query,
        "plan": "",
        "research_results": [],
        "analysis": "",
        "final_report": "",
        "sources": []
    }
    
    # Execute workflow synchronously
    result = workflow_app.invoke(initial_state)
    
    # Assertions to ensure each agent executed and updated the graph state
    assert result is not None
    assert "plan" in result
    assert "research_results" in result
    assert "analysis" in result
    assert "final_report" in result
    
    # Verify outputs are populated
    assert topic_query in result["plan"]
    assert len(result["research_results"]) > 0
    assert topic_query in result["analysis"]
    assert "# Executive Summary" in result["final_report"]
    assert "# Conclusion" in result["final_report"]
