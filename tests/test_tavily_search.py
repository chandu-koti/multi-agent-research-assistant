import pytest
from unittest.mock import MagicMock, patch
from src.tools.search_tool import TavilySearchTool
from src.agents.researcher import ResearchAgent
from src.models.schemas import ResearchState
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_tavily_search_tool_mapping() -> None:
    """
    Verify TavilySearchTool correctly maps fields from the Tavily API response.
    """
    mock_response = {
        "results": [
            {"title": "GCP Architecture", "url": "https://gcp.com", "content": "GCP Cloud overview"},
            {"title": "AWS Architecture", "url": "https://aws.com", "content": "AWS Cloud overview"}
        ]
    }
    
    with patch("src.tools.search_tool.TavilyClient") as mock_client_cls:
        mock_client_instance = MagicMock()
        mock_client_instance.search.return_value = mock_response
        mock_client_cls.return_value = mock_client_instance
        
        tool = TavilySearchTool(api_key="mock-key")
        results = tool.search("Cloud Computing")
        
        assert len(results) == 2
        assert results[0]["title"] == "GCP Architecture"
        assert results[0]["url"] == "https://gcp.com"
        assert results[0]["content"] == "GCP Cloud overview"

def test_tavily_search_tool_failure() -> None:
    """
    Verify TavilySearchTool raises RuntimeError when Tavily client throws exception.
    """
    with patch("src.tools.search_tool.TavilyClient") as mock_client_cls:
        mock_client_instance = MagicMock()
        mock_client_instance.search.side_effect = Exception("API Key Expired")
        mock_client_cls.return_value = mock_client_instance
        
        tool = TavilySearchTool(api_key="mock-key")
        with pytest.raises(RuntimeError) as exc_info:
            tool.search("test")
        assert "Tavily search request failed" in str(exc_info.value)

def test_researcher_agent_deduplication() -> None:
    """
    Verify ResearchAgent deduplicates search results by URL and populates state.
    """
    mock_results = [
        {"title": "GCP Architecture", "url": "https://gcp.com", "content": "First result"},
        {"title": "GCP Clone", "url": "https://gcp.com", "content": "Duplicate URL result"},
        {"title": "AWS Architecture", "url": "https://aws.com", "content": "Second result"}
    ]
    
    mock_llm = MagicMock()
    agent = ResearchAgent(llm=mock_llm)
    
    # Mock the internal search tool
    agent.search_tool = MagicMock()
    agent.search_tool.search.return_value = mock_results
    
    state: ResearchState = {
        "topic": "Cloud",
        "plan": '{"research_questions": ["Q1"]}',
        "research_results": [],
        "analysis": "",
        "final_report": "",
        "sources": []
    }
    
    output = agent.execute(state)
    
    assert len(output["sources"]) == 2  # Deduplicated from 3 to 2
    assert output["sources"][0]["url"] == "https://gcp.com"
    assert output["sources"][1]["url"] == "https://aws.com"
    
    assert len(output["research_results"]) == 2
    assert output["research_results"][0] == "First result"
    assert output["research_results"][1] == "Second result"

def test_researcher_agent_fallback() -> None:
    """
    Verify ResearchAgent executes fallback logic when Tavily search fails.
    """
    mock_llm = MagicMock()
    agent = ResearchAgent(llm=mock_llm)
    
    # Mock search to raise exception
    agent.search_tool = MagicMock()
    agent.search_tool.search.side_effect = Exception("Network Disconnection")
    
    state: ResearchState = {
        "topic": "Cloud",
        "plan": '{"research_questions": ["Q1"]}',
        "research_results": [],
        "analysis": "",
        "final_report": "",
        "sources": []
    }
    
    output = agent.execute(state)
    
    # Verifies graceful continuation
    assert len(output["sources"]) == 0
    assert len(output["research_results"]) == 1
    assert "Tavily search failed" in output["research_results"][0]

def test_api_source_count() -> None:
    """
    Verify the FastAPI POST /research endpoint returns source_count field.
    """
    # Force Tavily failure or mock workflow invoke to verify response shapes
    with patch("src.graph.workflow.app.ainvoke") as mock_ainvoke:
        mock_ainvoke.return_value = {
            "topic": "AI",
            "final_report": "# Report Content",
            "sources": [
                {"title": "Source 1", "url": "https://s1.com"},
                {"title": "Source 2", "url": "https://s2.com"}
            ]
        }
        
        response = client.post("/research", json={"topic": "AI"})
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "AI"
        assert data["source_count"] == 2
        assert data["execution_status"] == "completed"
