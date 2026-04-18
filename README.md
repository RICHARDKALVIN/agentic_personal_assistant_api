# Agentic Personal Assistant

An AI-powered assistant that can:
- handle general conversation,
- perform web-backed question answering,
- search hotels by constraints, and
- complete a hotel booking flow through a connected hotel API service.

This repository contains **two cooperating projects**:
- `personal_assistant` (Python/FastAPI + LangGraph orchestration)
- `hotel_booking_api` (Java/Spring Boot hotel search and booking API)

---

## Project Structure

```text
Agentic Personal Assistant/
├─ personal_assistant/
│  ├─ app/
│  │  ├─ api/                # FastAPI route layer
│  │  ├─ services/           # Chat service orchestration
│  │  ├─ graph/              # LangGraph workflow and nodes
│  │  ├─ memory/             # Redis short-term memory + summarization
│  │  ├─ web_search/         # Serper + scraping + answer synthesis
│  │  ├─ llm/                # LLM provider setup
│  │  ├─ schemas/            # Pydantic and graph state schemas
│  │  ├─ core/               # Shared infra clients (Redis)
│  │  └─ trace/              # Langfuse setup
│  ├─ docker-compose.yml     # Redis + Chroma local services
│  └─ requirements.txt
└─ hotel_booking_api/
   └─ hotel_book/hotel_book/
      ├─ src/main/java/...   # Spring Boot controller/service/models
      └─ pom.xml
```

---

## High-Level Architecture

1. Client sends a message to `POST /chat/` (Python service).
2. Assistant loads recent and summarized memory from Redis.
3. Query is rewritten into a standalone form.
4. LangGraph classifies intent and routes to one of:
   - general conversation reply,
   - web search answer,
   - reservation flow (with field checks),
   - follow-up booking flow.
5. For hotel operations, Python service calls Java hotel API on port `8080`.
6. Response is returned to client and stored in Redis memory.
7. Every 3 messages, conversation summary is refreshed.

---

## End-to-End Flow (Detailed)

### 1) API Entry
- File: `personal_assistant/app/api/chat.py`
- Endpoint: `POST /chat/`
- Input schema (`ChatRequest`):
  - `user_id`
  - `session_id`
  - `message`
- Passes request to `chat_service.chat(...)` with Langfuse callback handler.

### 2) Chat Service Orchestration
- File: `personal_assistant/app/services/chat_service.py`
- Steps:
  1. Builds tracing config metadata (`langfuse_user_id`, `langfuse_session_id`).
  2. Loads STM messages + summary from Redis (`RedisSTM`).
  3. Rewrites the user query using LLM (`get_re_written_query`).
  4. Builds conversation context prompt (`build_prompt`).
  5. Invokes LangGraph app with `AgentState`.
  6. Persists user + assistant messages back to Redis.
  7. Increments message counter; every 3rd message triggers summary refresh.

### 3) Graph Routing Logic
- Files:
  - `personal_assistant/app/graph/graph.py`
  - `personal_assistant/app/graph/nodes/graph_nodes.py`
  - `personal_assistant/app/graph/nodes/graph_helper_functions.py`

Graph nodes:
- `intent_router` -> classify input into structured intent.
- `general_conv` -> respond to non-task conversational queries.
- `field_check` -> validate reservation essentials (`city`, `check_in`).
- `hotel_search` -> call hotel search API and format options.
- `get_human_response` -> store session state for follow-up booking.
- `follow_up` -> reload saved state.
- `book_hotel` -> call booking API.
- `web_search` -> query web and synthesize answer.

Routing decisions:
- `is_follow_up` -> follow-up path
- `is_general` -> general conversation
- `is_reservation` -> reservation path
- `need_web_search` -> web search path

### 4) Memory Model
- File: `personal_assistant/app/memory/RedisSTM.py`
- Maintains:
  - rolling recent messages (`stm:{user_id}:messages`, trimmed to recent window),
  - summary (`stm:{user_id}:summary`),
  - periodic summarization via LLM.

### 5) Hotel Search/Booking Backend
- Java API location: `hotel_booking_api/hotel_book/hotel_book`
- Controller: `HotelController`
  - `POST /api/hotels/search`
  - `POST /api/hotels/book/{id}/{name}`
- Service: `HotelService`
  - filters in-memory hotel list by city, budget range, and guest count
  - returns booking confirmation or not found.

### 6) Web Search Path
- File: `personal_assistant/app/web_search/search.py`
- Flow:
  1. Query Serper API,
  2. scrape top links,
  3. summarize answer through OpenRouter model response.

---

## Request Routing Flowchart

```mermaid
flowchart TD
    A[POST /chat/] --> B[Load Redis memory + summary]
    B --> C[Rewrite user query]
    C --> D[LangGraph intent_router]

    D -->|is_general| E[general_conv]
    D -->|need_web_search| F[web_search]
    D -->|is_reservation| G[field_check]
    D -->|is_follow_up| H[follow_up]

    G -->|missing required fields| I[Ask user for missing info]
    G -->|ready| J[hotel_search]
    J --> K[Persist state for follow-up]
    K --> L[Return hotel options]

    H -->|action=book_hotel| M[book_hotel]
    H -->|otherwise| N[End]

    E --> O[Store messages in Redis]
    F --> O
    I --> O
    L --> O
    M --> O
```

---

## Tech Stack

### `personal_assistant` (Python)
- FastAPI
- LangChain + LangGraph
- Redis (conversation memory/state)
- ChromaDB (vector store utilities present)
- Gemini models (intent/rewrite/summarization path)
- OpenRouter (response formatting and web-answer synthesis)
- Langfuse (tracing/observability)

### `hotel_booking_api` (Java)
- Spring Boot (Web MVC)
- Lombok
- Maven
- Java 17

---

## Prerequisites

- Python 3.10+
- Java 17+
- Maven 3.9+ (or use Maven wrapper included in project)
- Docker Desktop (for Redis and Chroma containers)

---

## Environment Variables

Create a `.env` file inside `personal_assistant/` with at least:

```env
# LLM and routing
GEMINI_API_KEY=your_gemini_key
OPEN_ROUTER_URL=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_API_KEY=your_openrouter_key
XAI_API_KEY=your_xai_key

# Web search
SERPER_URL=https://google.serper.dev/search
SERPER_API_KEY=your_serper_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional SQL utility (if used by db_engine.py)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Langfuse tracing
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

---

## Local Setup and Run

### 1) Start infrastructure services (Redis + Chroma)

```bash
cd personal_assistant
docker compose up -d
```

### 2) Run hotel booking API (Java)

```bash
cd hotel_booking_api/hotel_book/hotel_book
./mvnw spring-boot:run
```

On Windows PowerShell:

```powershell
cd hotel_booking_api/hotel_book/hotel_book
.\mvnw.cmd spring-boot:run
```

Default URL: `http://localhost:8080`

### 3) Run personal assistant API (Python)

```bash
cd personal_assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On Windows PowerShell:

```powershell
cd personal_assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API base URL: `http://localhost:8000`

---

## API Reference

### Personal Assistant API

#### `POST /chat/`

Request body:

```json
{
  "user_id": "user-123",
  "session_id": "sess-001",
  "message": "Book a hotel in Chennai tomorrow for 2 guests under 2000"
}
```

Response body:

```json
{
  "user_id": "user-123",
  "session_id": "sess-001",
  "response": "..."
}
```

### Hotel API

#### `POST /api/hotels/search`
Example request:

```json
{
  "city": "Chennai",
  "check_in": "2026-04-19",
  "check_out": "2026-04-20",
  "budget": 2000,
  "guests": 2
}
```

#### `POST /api/hotels/book/{id}/{name}`
Example:
- `/api/hotels/book/1/Grand Palace`

---

## Important Notes

- Both services must run together for reservation and booking paths.
- Python service currently calls Java service at hardcoded `http://localhost:8080`.
- Session continuity and follow-up booking depend on Redis being available.
- ChromaDB is provisioned and utility modules exist, though retrieval flow is not yet wired into the main chat graph.

---

## Suggested Improvements

- Add centralized config file for service URLs and model names.
- Add API auth and rate-limiting.
- Add robust validation/error handling for external API failures.
- Add unit/integration tests for graph-node transitions.
- Add CI pipeline for Python + Java services.

---

