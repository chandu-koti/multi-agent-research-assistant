# Multi-Agent AI Research Assistant Foundation

This project establishes a production-ready, clean, and extensible architectural foundation for a Multi-Agent AI Research Assistant. It is designed using Python, FastAPI, LangGraph, LangChain, and Pydantic.

## Tech Stack & Architecture

- **FastAPI**: Modern, fast web framework for building APIs.
- **LangGraph**: State machine library for building multi-agent cyclic/acyclic flows.
- **Pydantic Settings**: Hierarchical application configuration loading from environment variables.
- **Structured Logging**: Clean logging format aligned with production standards.

### Directory Structure

```
multi-agent-research-assistant/
├── .env.example
├── requirements.txt
├── README.md
├── src/
│   ├── main.py
│   ├── agents/
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── analyzer.py
│   │   └── writer.py
│   ├── graph/
│   │   └── workflow.py
│   ├── tools/
│   │   └── search_tool.py
│   ├── api/
│   │   └── routes.py
│   ├── models/
│   │   └── schemas.py
│   └── core/
│       ├── config.py
│       └── logging.py
└── tests/
```

### LangGraph Agent Workflow Sequence

The workflow is a linear pipeline represented as follows:

```
  [START]
     │
     ▼
┌──────────────┐
│ PlannerAgent │
└──────┬───────┘
       │
       ▼
┌───────────────┐
│ ResearchAgent │
└──────┬────────┘
       │
       ▼
┌───────────────┐
│ AnalysisAgent │
└──────┬────────┘
       │
       ▼
┌─────────────┐
│ WriterAgent │
└──────┬──────┘
       │
       ▼
   [END]
```

---

## Setup & Running

### 1. Installation

Create a virtual environment and install dependencies:

```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and configure settings:

```bash
cp .env.example .env
```

### 3. Running the Server

Start the FastAPI application:

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 4. Interactive API Documentation

Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to view Swagger UI.

### 5. Running Tests

Run test suites using:

```bash
pytest
```
