from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check() -> None:
    """
    Test the server health check API endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_research_endpoint() -> None:
    """
    Test POST /research endpoint with mock payload.
    """
    payload = {"topic": "Quantum Computing"}
    response = client.post("/research", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["topic"] == "Quantum Computing"
    assert "report" in data
    assert data["execution_status"] == "completed"
    
    # Assert headers in the report exist as specified in templates
    report_text = data["report"]
    assert "# Executive Summary" in report_text
    assert "# Research Questions" in report_text
    assert "# Key Findings" in report_text
    assert "# Opportunities" in report_text
    assert "# Risks" in report_text
    assert "# Future Trends" in report_text
    assert "# Conclusion" in report_text
