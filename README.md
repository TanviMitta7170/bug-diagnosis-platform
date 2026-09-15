# Creation of Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance

> Individual Capstone Project — B.Tech CSE (AI & ML), Vardhaman College of Engineering

An intelligent multi-agent platform that transforms raw bug reports and error logs into structured, actionable resolution guidance — powered by a growing historical defect knowledge base.

---

## Overview

Software development teams repeatedly waste time investigating bugs that have already been solved. Developers manually parse stack traces, try to recall past fixes, and rediscover solutions that exist in the team's own history.

This platform eliminates that by running every submitted bug report through a pipeline of five specialized AI agents that automatically triage, analyze, detect duplicates, identify root causes, and recommend fixes — all grounded in historical bug data rather than generic guesswork.

Unlike asking a generic LLM, this system remembers your team's past bugs, learns from resolved issues, and delivers structured consistent output — not just a chat response.

---

## Features

| Feature | Description |
|---|---|
| **Bug Analyzer** | Submit a stack trace or upload a log file (.txt/.log). Five agents analyze it sequentially with a live pipeline status indicator and confidence scores. |
| **Triage Agent** | Classifies severity (Critical/High/Medium/Low), priority (P1–P4), affected component, user impact, and confidence score with reasoning. |
| **Log Analysis Agent** | Parses stack traces to extract exception type, exact failure point, call chain, and diagnostic signal. |
| **Duplicate Detection Agent** | Searches the knowledge base for historically similar bugs and returns similarity scores with past resolutions. |
| **Root Cause Agent** | Reasons about the probable root cause grounded in log analysis and historical context, with a confidence score and supporting evidence. |
| **Remediation Agent** | Recommends numbered fix steps, effort estimate, reviewer suggestion, and prevention tip — grounded in historical resolutions. |
| **Dashboard** | KPI metrics (total, open, resolved, resolution rate), severity distribution, component breakdown, and priority charts. |
| **Bug Prediction** | Paste a git commit diff to predict bug risk (High/Medium/Low) with risk score, vulnerable areas, and recommended tests. |
| **Bug Chat** | Conversational interface — ask questions about past bugs in plain English, answered from the knowledge base. Unanswered queries are automatically saved for future reference. |
| **Knowledge Base** | Search and filter all historical bugs by severity and component. View full details and add newly resolved bugs to improve future recommendations. |
| **Bug History** | Every analysis is saved automatically. Mark bugs as resolved with applied fix and resolution notes. Search and filter past analyses. |
| **Sample Cases** | Four pre-loaded bug examples for instant demo — NullPointerException, DB connection timeout, Python KeyError, React TypeError. |

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | Streamlit (Python) | Pure Python stack, fast to build, clean interface |
| Backend API | FastAPI (Python) | Async support, auto-generates API docs |
| LLM Provider | Groq API | Free tier, low latency inference |
| Data Storage | JSON files | Simple, no database setup required |
| Charts | Plotly | Interactive charts in Streamlit |
| Environment | Python venv | Dependency isolation |

---

## Project Structure

```
mittatanvi_Creation of Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Environment variables (GROQ_API_KEY, model, paths)
│   ├── requirements.txt           # All Python dependencies
│   ├── agents/
│   │   ├── triage_agent.py        # Severity, priority, component, confidence
│   │   ├── log_agent.py           # Stack trace parsing
│   │   ├── duplicate_agent.py     # Historical similarity search
│   │   ├── root_cause_agent.py    # Root cause reasoning with KB context
│   │   ├── remediation_agent.py   # Fix recommendation grounded in history
│   │   ├── prediction_agent.py    # Git commit risk analysis
│   │   └── chat_agent.py          # NL question answering over KB
│   ├── routes/
│   │   ├── analyze.py             # POST /api/analyze — runs all 5 agents
│   │   ├── knowledge.py           # Knowledge base CRUD
│   │   ├── predict.py             # POST /api/predict
│   │   ├── chat.py                # POST /api/chat
│   │   └── history.py             # Bug history routes
│   ├── models/
│   │   ├── bug_report.py          # Pydantic input models
│   │   └── analysis_result.py     # Pydantic output models
│   └── data/
│       ├── seed_bugs.json         # Historical bug knowledge base (14 bugs)
│       └── bug_history.json       # Past analysis sessions
└── frontend/
    ├── app.py                     # Streamlit home page with sidebar
    └── pages/
        ├── 1_Bug_Analyzer.py      # Main analysis page with sample cases
        ├── 2_Dashboard.py         # Charts and KPI metrics
        ├── 3_Bug_Prediction.py    # Commit risk analysis
        ├── 4_Bug_Chat.py          # Conversational interface
        ├── 5_Knowledge_Base.py    # Search, filter, add bugs
        └── 6_Bug_History.py       # Past analyses with resolution tracking
```

---

## Setup and Installation

### Prerequisites
- Python 3.11 or 3.12
- A Groq API key — free at https://console.groq.com

### 1. Clone the repository
```bash
git clone https://github.com/TanviMitta7170/bug-diagnosis-platform.git
cd bug-diagnosis-platform
```

### 2. Set up the backend
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure your API key
Create a `.env` file inside the `backend/` folder:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Start the backend
```bash
uvicorn main:app --reload --port 8001
```

You should see:
```
Uvicorn running on http://127.0.0.1:8001
```

API documentation is available at `http://127.0.0.1:8001/docs`

### 5. Start the frontend
Open a second terminal:
```bash
cd frontend
pip install streamlit requests plotly
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Health check — returns bug count and API status |
| POST | /api/analyze | Run full 5-agent pipeline on a bug report |
| POST | /api/predict | Analyze a git commit diff for bug risk |
| POST | /api/chat | Ask a question answered from the knowledge base |
| GET | /api/knowledge/bugs | List all bugs in the knowledge base |
| GET | /api/knowledge/count | Get total bug count |
| POST | /api/knowledge/add | Add a resolved bug to the knowledge base |
| GET | /api/history/all | List all past analysis sessions |
| POST | /api/history/add | Save a new analysis to history |
| PUT | /api/history/resolve/{id} | Mark a bug as resolved with notes |
| DELETE | /api/history/{id} | Delete a history entry |

---

## Agent Pipeline

When a bug report is submitted, the backend runs all five agents in sequence — each agent's output feeds into the next:

```
Bug Submission
      │
      ▼
1. Triage Agent          → severity, priority, component, confidence score
      │
      ▼
2. Log Analysis Agent    → exception type, failure point, call chain
      │
      ▼
3. Duplicate Detection   → similar historical bugs, similarity scores
      │
      ▼
4. Root Cause Agent      → probable cause grounded in log + KB context
      │
      ▼
5. Remediation Agent     → numbered fix steps, effort, reviewer, prevention tip
      │
      ▼
Structured output displayed in Streamlit + saved to Bug History
```

---

## Development Methodology

Built using Agile methodology with weekly sprints. Each sprint delivered a working, demonstrable increment.

| Sprint | Scope | Status |
|---|---|---|
| Sprint 1 | Project structure, FastAPI, Streamlit skeleton, JSON knowledge base, 10 seed bugs | Complete |
| Sprint 2 | All 5 agents with Groq API, /api/analyze route, Bug Analyzer page, file upload | Complete |
| Sprint 3 | Dashboard, Bug Prediction, Bug Chat, Bug History, Resolution Tracking, Sample Cases | Complete |
| Sprint 4 | Testing, error handling, port configuration, additional bugs, demo preparation | Complete |

---

## Testing

Errors encountered and resolved during development:

- `ModuleNotFoundError: No module named 'backend'` — fixed by running uvicorn from inside the `backend/` folder
- `pydantic-core` build failure on Python 3.13 — fixed by upgrading to `pydantic>=2.8.0` which has pre-built wheels
- Gemini API deprecation warning — migrated from `google.generativeai` to `google.genai`
- Port conflict with another project on 8000 — resolved by running on port 8001
- LLM returning markdown-wrapped JSON — fixed by stripping code fences before `json.loads()`
- `scipy` DLL blocked by Application Control policy — resolved by removing `sentence-transformers` dependency and using LLM-based similarity instead

---

## Author

**Tanvi**
Roll No: 24881A66A0
B.Tech CSE (AI & ML) — Vardhaman College of Engineering, Hyderabad
GitHub: [github.com/TanviMitta7170](https://github.com/TanviMitta7170)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
