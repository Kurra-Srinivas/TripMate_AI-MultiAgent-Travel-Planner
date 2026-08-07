# 🌐 Agentic Travel Planner (TripMate AI)
### Production-Grade Multi-Agent Orchestration Engine with LangGraph, Model Context Protocol (MCP), Input Guardrails, Human-in-the-Loop (HITL), & PostgreSQL State Persistence

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2.2-orange.svg)](https://python.langchain.com/docs/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Llama--3.3--70B-purple.svg)](https://groq.com/)
[![Tavily](https://img.shields.io/badge/Tavily-MCP__Search-blueviolet.svg)](https://tavily.com/)
[![OpenWeather](https://img.shields.io/badge/OpenWeather-MCP__Server-yellow.svg)](https://openweathermap.org/)
[![AviationStack](https://img.shields.io/badge/AviationStack-Flight__API-red.svg)](https://aviationstack.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Render__DB-blue.svg)](https://www.postgresql.org/)
[![Render](https://img.shields.io/badge/Render-Cloud__Deployment-black.svg)](https://render.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 📌 Executive Summary

**Agentic Travel Planner** is an enterprise-grade multi-agent travel orchestration engine designed to model, route, evaluate, and finalize complex travel itineraries. Built using **LangGraph**, **Model Context Protocol (MCP)**, **FastAPI**, and **PostgreSQL State Checkpointing**, the system coordinates specialized AI agent nodes through a supervisor router, enforces safety input guardrails, queries live APIs, performs financial feasibility analysis, and supports Human-in-the-Loop (HITL) review cycles.

---

## 🏛️ System Architecture & Workflow

```
                        ┌────────────────────────┐
                        │   User Request (UI/API)│
                        └───────────┬────────────┘
                                    │
                                    ▼
                        ┌────────────────────────┐
                        │   Input Guardrail Check │
                        └──────┬───────────┬─────┘
                               │           │
                     [Blocked] │           │ [Allowed]
                               ▼           ▼
             ┌──────────────────┐   ┌───────────────────────────┐
             │ Guardrail Blocked│   │  Supervisor Agent Node    │
             └────────┬─────────┘   └─────────────┬─────────────┘
                      │                           │
                      │               ┌───────────┴───────────┐
                      │               ▼                       ▼
                      │     ┌──────────────────┐    ┌──────────────────┐
                      │     │  Flight Agent    │    │   Hotel Agent    │
                      │     └────────┬─────────┘    └────────┬─────────┘
                      │              │                       │
                      │              └───────────┬───────────┘
                      │                          ▼
                      │             ┌──────────────────────────┐
                      │             │   Weather MCP Agent      │
                      │             └────────────┬─────────────┘
                      │                          ▼
                      │             ┌──────────────────────────┐
                      │             │   Budget Analyst Agent   │
                      │             └────────────┬─────────────┘
                      │                          ▼
                      │             ┌──────────────────────────┐
                      │             │  Itinerary Generator     │
                      │             └────────────┬─────────────┘
                      │                          ▼
                      │             ┌──────────────────────────┐
                      │             │ Human-in-the-Loop (HITL) │
                      │             │     Approval Node        │
                      │             └────────────┬─────────────┘
                      │                          │
                      │              [Approve /  │
                      │               Revision]  ▼
                      │             ┌──────────────────────────┐
                      │             │   Final Response Agent   │
                      │             └────────────┬─────────────┘
                      │                          │
                      └──────────────────────────┴────────────► [ End Output ]
```

---

## 🔑 Key Technical Features

1. **Supervisor Orchestration Routing**: Dynamically parses input requirements, extracts trip constraints (destination, origin, budget, duration), and routes work only to required specialist agent nodes.
2. **Input Guardrail Safety Filter**: Intercepts un-related or unsafe prompts before execution, returning structured block messages to protect backend tools.
3. **Model Context Protocol (MCP) Integration**: Communicates via standard stdio and streamable HTTP transport with external tool providers (Tavily search, AviationStack flight status, OpenWeather MCP server).
4. **Budget Analyst Specialist**: Evaluates financial feasibility, compares estimated flight/hotel expenses against budget limits, and flags cost risks with feasibility scores.
5. **Human-in-the-Loop (HITL) Interrupts**: Pauses state execution after draft itinerary generation, enabling users to approve the plan or supply feedback for instant revision.
6. **PostgreSQL Checkpointing & Resilience**: Uses `PostgresSaver` to persist graph state across sessions, with automatic fallback to `MemorySaver` during offline local development.
7. **Production Containerization**: Fully dockerized with multi-stage build optimizations and non-root execution support for Render Web Services.

---

## 📂 Project Repository Structure

```
agentic-travel-planner/
├── app.py                         # FastAPI Web Application & API Endpoints
├── backend.py                     # LangGraph State Graph & Node Assembly
├── mcp_client.py                  # MultiServerMCPClient & Model Definitions
├── custom_weather_mcp_server.py   # Root Weather FastMCP Server Entrypoint
├── Dockerfile                     # Production Docker Image Configuration
├── requirements.txt               # Project Dependencies
├── README.md                      # Comprehensive Documentation
├── architecture.md                # System Architecture & Technical Specifications
├── LICENSE                        # Project License
├── agents/                        # Modular Agent Nodes
│   ├── __init__.py
│   ├── guardrails.py              # Input Guardrail Logic & Handler Node
│   ├── supervisor.py              # Supervisor Router & Constraint Extractor
│   └── budget_agent.py            # Financial Feasibility Analyst Node
├── tools/                         # Custom Tool & API Adapters
│   ├── __init__.py
│   ├── flight_tool.py             # AviationStack REST & IATA Lookup Tool
│   └── tavily_tool.py             # Tavily Web Search Tool Wrapper
├── mcp_servers/                   # MCP Server Modules
│   ├── __init__.py
│   └── custom_weather_mcp_server.py # FastMCP OpenWeather Server
├── tests/                         # Test Suite & Runner Scripts
│   ├── __init__.py
│   ├── test_endpoints.py          # Automated FastAPI Unit Tests
│   ├── test_mcp_client.py         # MCP Client Configuration Tests
│   └── test_api.py                # Interactive CLI Test Runner
├── static/                        # Frontend Stylesheets & Client Scripts
│   ├── style.css
│   └── script.js
├── templates/                     # Jinja2 HTML Templates
│   └── index.html
└── excalidraw_files/              # System Architecture Visual Assets
    └── architecture.excalidraw
```

---

## ⚙️ Environment Variables & Configuration

Create a `.env` file in the project root:

```env
# Required API Keys
GROQ_API_KEY=gsk_your_groq_api_key_here
TAVILY_API_KEY=tvly-your_tavily_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
AVIATIONSTACK_API_KEY=your_aviationstack_api_key_here

# Default Origin Airport (IATA Code)
DEFAULT_ORIGIN_IATA=DEL

# Database Persistence URL (Render PostgreSQL or local pgAdmin)
DATABASE_URL=postgres://user:password@ep-xyz.render.com/travel_db
```

---

## 🛠️ Quick Start Guide (Local Setup)

### 1. Clone & Setup Environment
```powershell
# Clone repository
git clone https://github.com/YOUR_USERNAME/agentic-travel-planner.git
cd agentic-travel-planner

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Windows PowerShell
```

### 2. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run Automated Tests
```powershell
python -m unittest discover -s tests
```

### 4. Run Interactive Web Application
```powershell
python app.py
```
Open `http://localhost:8000` in your web browser.

---

## 🐳 Docker Deployment

### Build Image
```powershell
docker build -t agentic-travel-planner .
```

### Run Container
```powershell
docker run -p 8000:8000 --env-file .env agentic-travel-planner
```

---

## ☁️ Deploying to Render Web Services

1. **Push Code to GitHub**:
   ```powershell
   git add .
   git commit -m "Production deployment build"
   git push origin main
   ```
2. **Create Render PostgreSQL Database**:
   - Go to [Render Dashboard](https://dashboard.render.com/) -> **New +** -> **PostgreSQL**.
   - Copy the **Internal / External Database URL**.
3. **Create Render Web Service (Docker Runtime)**:
   - Click **New +** -> **Web Service** -> Connect your GitHub repo.
   - Set **Runtime**: `Docker`.
   - In **Environment Variables**, add:
     - `GROQ_API_KEY`
     - `TAVILY_API_KEY`
     - `OPENWEATHER_API_KEY`
     - `AVIATIONSTACK_API_KEY`
     - `DEFAULT_ORIGIN_IATA` (`DEL`)
     - `DATABASE_URL`

---

## 📖 API Reference

### 1. `POST /api/travel`
Start a new travel planning thread.
- **Request Body**:
  ```json
  {
    "message": "Plan a 5 day trip to Tokyo from Delhi under $2000",
    "thread_id": "optional_custom_thread_id"
  }
  ```

### 2. `POST /api/travel/approve`
Approve or request revision for a draft itinerary.
- **Request Body**:
  ```json
  {
    "thread_id": "user_xyz",
    "approved": false,
    "feedback": "Add vegetarian food options on Day 2 and Day 3"
  }
  ```

### 3. `GET /health`
Returns system status and enabled agent features.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
