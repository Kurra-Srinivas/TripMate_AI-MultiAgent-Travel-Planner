# 🏗️ Deep-Dive Technical Architecture Specification
## Agentic Travel Planner (TripMate AI)

This document provides a comprehensive technical architecture overview of the **Agentic Travel Planner**, detailing the multi-agent graph state machine, Model Context Protocol (MCP) server/client interactions, security guardrails, Human-in-the-Loop (HITL) execution controls, database persistence, and fault-tolerance design patterns.

---

## 1. High-Level Architecture Overview

The system is designed around a **Directed Cyclic State Graph** powered by **LangGraph**. Unlike traditional monolithic LLM chains, this architecture decomposes complex travel planning into specialized autonomous agents coordinated by a **Supervisor Router**.

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

## 2. Core Architectural Components

### 2.1 Input Guardrails (`agents/guardrails.py`)
- **Purpose**: Intercept prompt injections, malicious requests, or non-travel queries before invoking specialist LLM calls or third-party search APIs.
- **Execution Flow**:
  1. The user query is passed to `input_guardrail_check(query, llm)`.
  2. Prompt evaluates whether the request falls under valid travel categories (destinations, flights, hotels, weather, budget, visas, sightseeing).
  3. Returns a strict JSON payload: `{"allowed": true/false, "reason": "..."}`.
  4. If blocked, execution routes directly to `guardrail_blocked_agent`, returning a structured safety explanation and terminating the graph.

---

### 2.2 Supervisor Router (`agents/supervisor.py`)
- **Purpose**: Act as the central intelligence orchestrator of the multi-agent network.
- **Execution Flow**:
  1. Receives `user_query` and graph state.
  2. Extracts trip constraints: `destination`, `origin`, `duration`, `budget`, `travel_style`, and `special_preferences`.
  3. Evaluates which specialist nodes are required for the query:
     - `flight_agent`: Required for flight search, routes, airlines, and airport advice.
     - `hotel_agent`: Required for accommodations and neighborhood guidance.
     - `weather_agent`: Required for seasonal climate and forecast information.
     - `budget_agent`: Required for cost feasibility analysis.
     - `itinerary_agent`: Always included to integrate specialist output into a cohesive plan.
  4. Stores `selected_agents` list in state and dynamically dictates graph routing sequence.

---

### 2.3 Specialist Tools & MCP Servers

#### A. Custom Tools (`tools/flight_tool.py` & `tools/tavily_tool.py`)
- **Flight Tool**: Resolves location names/cities to IATA codes (`resolve_location_to_iata`), determines departure/arrival airports, and queries AviationStack API or provides hub routing options. Defaults origin to `DEL` (Delhi) when unspecified.
- **Tavily Tool**: Performs web search for live hotel accommodations, pricing ranges, and local destination highlights.

#### B. Custom Weather FastMCP Server (`mcp_servers/custom_weather_mcp_server.py`)
- Built using **FastMCP**.
- Exposes tools:
  - `get_current_weather(city)`: Fetches current temperature, humidity, condition, and wind speed.
  - `get_forecast(city)`: Fetches 5-period forecast details.
- Runs as a stdio subprocess spawned dynamically by `MultiServerMCPClient`.

---

### 2.4 Human-in-the-Loop (HITL) State Machine
- **Node**: `human_approval_agent` in `backend.py`.
- **Implementation**:
  ```python
  review = interrupt({
      "question": "Do you approve this itinerary?",
      "draft_itinerary": state.get("itinerary", ""),
      "approval_request": state.get("approval_request", ""),
  })
  ```
- **Behavior**:
  1. Execution halts completely after `itinerary_agent` drafts the plan.
  2. State checkpoint is serialized and stored in PostgreSQL / MemorySaver.
  3. The frontend displays the draft plan with interactive **Approve** and **Request Revision** options.
  4. When the user submits approval or revision feedback, `resume_travel_agent(thread_id, approved, feedback)` resumes execution using `Command(resume=...)`.

---

### 2.5 Database State Checkpointing & Persistence (`backend.py`)
- **Primary Checkpointer**: `PostgresSaver` from `langgraph.checkpoint.postgres`.
- **Render PostgreSQL Support**:
  - Automatically parses Render database connection strings, converting `postgres://` to `postgresql://` and enforcing `sslmode=require`.
- **Graceful Offline Fallback**:
  - If `DATABASE_URL` is missing or PostgreSQL fails to connect during local development, `init_checkpointer()` gracefully falls back to `MemorySaver()` without throwing unhandled exceptions.

---

## 3. Data State Schema (`TravelState`)

The central graph state dictionary contains the following typed attributes:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `messages` | `Annotated[list[AnyMessage], operator.add]` | Message history list appended across graph steps |
| `user_query` | `str` | Raw input prompt submitted by traveler |
| `guardrail_allowed` | `bool` | Whether query passed safety validation |
| `guardrail_reason` | `str` | Reason message if guardrail blocked query |
| `selected_agents` | `list[str]` | Specialist agent nodes selected by Supervisor |
| `trip_constraints` | `dict[str, Any]` | Extracted constraints (`destination`, `budget`, etc.) |
| `flight_results` | `str` | Flight route recommendations generated by `flight_agent` |
| `hotel_results` | `str` | Hotel search data generated by `hotel_agent` |
| `weather_results` | `str` | Live weather & forecast generated by `weather_agent` |
| `budget_results` | `str` | Financial feasibility analysis generated by `budget_agent` |
| `itinerary` | `str` | Integrated draft itinerary created by `itinerary_agent` |
| `approved` | `bool` | Human review decision |
| `human_feedback` | `str` | User revision feedback submitted during HITL interrupt |
| `final_response` | `str` | Final polished travel response delivered to user |

---

## 4. Fault Tolerance & Fallback Matrix

| Subsystem | Potential Failure Mode | Automatic Fallback Mechanism |
| :--- | :--- | :--- |
| **PostgreSQL DB** | Host unreachable or password failure | Falls back to in-memory `MemorySaver()` checkpointer |
| **OpenWeather API** | Invalid key or network timeout | Returns structured mock weather data with seasonal guidance |
| **AviationStack MCP** | `uvx` process error on Windows | Falls back to direct REST API route lookup tool |
| **Tavily MCP API** | Rate limit or key failure | Returns non-live general accommodation guidance |
| **Supervisor Parser** | LLM outputs invalid JSON | Selects full specialist agent pipeline as safe default |
