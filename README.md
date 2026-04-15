# Agentic Personal Assistant

A FastAPI-based, memory-enabled conversational assistant for hotel discovery and booking flow orchestration using LangGraph.

## What This Application Does

This service accepts user chat messages, rewrites them into standalone queries, classifies intent, and routes the request through a graph-based workflow to:

- respond to general conversation,
- collect missing reservation details,
- list matching hotels,
- or confirm a follow-up booking action.

It also stores short-term chat memory in Redis and periodically generates a rolling conversation summary.

## Tech Stack 

Core external libraries used in the current runtime path:

- `fastapi`, `uvicorn` - API layer and ASGI server
- `pydantic` - request/response and structured intent schema validation
- `langgraph` - stateful workflow graph orchestration
- `langchain-core`, `langchain-google-genai`, `langfuse` - LLM integration and tracing
- `openai` - xAI/Grok-compatible client for response generation
- `redis` (async client) - short-term memory and summary storage
- `python-dotenv` - environment variable loading
- `loguru` - structured logging



## High-Level Architecture

`/chat` request lifecycle:

1. API endpoint receives `user_id`, `session_id`, and `message`.
2. `chat_service` loads memory from Redis (recent messages + summary).
3. Query is rewritten into a standalone form using a Gemini model.
4. Context prompt is built from summary + short-term history + rewritten query.
5. LangGraph runs with `AgentState` and routes to one of the nodes based on classified intent.
6. Final response is returned to user and persisted into Redis memory.
7. Every 3 messages, a summary refresh is generated and saved.

## Workflow Graph (Execution Flow)

Entry node: `intent_router`

- **`intent_router_node`**
  - Uses structured LLM output (`IntentResponse`) to classify:
    - `is_general`
    - `is_reservation`
    - `is_follow_up`
    - extracted fields (`city`, `locality`, `hotel_name`, `date_and_time`)

Conditional routing:

- If `is_follow_up` -> `book_hotel_node`
- Else if `is_general` -> `general_conv_node`
- Else if `is_reservation` -> `field_check_node`
- Else -> `END`

Reservation branch:

- **`field_check_node`**
  - Validates required fields (`city`, `date_and_time`)
  - If missing, asks user for missing information
  - If complete, routes to `list_hotel_node`

- **`list_hotel_node`**
  - Retrieves matches from `get_restaurants(...)` (currently static in-memory dataset)
  - Uses Grok model via xAI-compatible OpenAI client to format a user-friendly hotel selection reply

Follow-up branch:

- **`book_hotel_node`**
  - Produces booking confirmation style response and follow-up assistance prompt

General branch:

- **`general_conv_node`**
  - Returns precomputed general reply from intent model

## Project Structure

```text
personal_assistant/
  app/
    api/chat.py                    # /chat endpoint
    services/chat_service.py       # main request orchestration
    graph/graph.py                 # LangGraph definition
    graph/nodes/graph_nodes.py     # workflow node logic
    graph/nodes/graph_helper_functions.py
    memory/RedisSTM.py             # short-term memory + summary
    llm/provider.py                # Gemini + Grok clients
    core/redis.py                  # Redis client config
    schemas/chat_schemas.py        # request/response + intent schema
    schemas/graph_state.py         # graph state schema
    utils/prompts.py               # prompt builder
    utils/query_util.py            # query rewriter
    utils/tools.py                 # static hotel dataset/filtering
    db/chroma_db.py                # vector store setup (auxiliary)
    db/db_engine.py                # SQL DB utility (auxiliary)
    trace/trace.py                 # Langfuse tracing setup
  docker-compose.yml               # Redis + Chroma services
  requirements.txt
```

## API Contract

### POST `/chat/`

Request body:

```json
{
  "user_id": "user-123",
  "session_id": "session-abc",
  "message": "Book me a hotel in Mumbai tomorrow"
}
```

Response body:

```json
{
  "response": "..."
}
```

## Environment Variables

Create a `.env` file in project root:

```env
# LLMs
GEMINI_API_KEY=your_gemini_key
XAI_API_KEY=your_xai_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Langfuse (optional but used by tracing setup)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com

# Optional (used by db_engine.py if enabled)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

## Local Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start infrastructure (Redis + Chroma):

```bash
docker compose up -d
```

3. Run the API:

```bash
uvicorn app.main:app --reload
```

4. Open API docs:

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Memory Behavior

- Recent messages are stored in Redis list `stm:{user_id}:messages`.
- Only the latest 6 messages are retained in short-term memory.
- Summary is stored in `stm:{user_id}:summary`.
- A message counter key (`count:messages:{user_id}`) triggers re-summarization every 3 new messages.

## Observability and Logging

- Logs are written to `logs/app.log` and stderr.
- Langfuse callback metadata includes:
  - `langfuse_user_id`
  - `langfuse_session_id`

## Important Notes

- Current hotel lookup (`get_restaurants`) is static mock data; no real booking backend is integrated yet.
- Chroma and SQL modules are present but not currently connected to the main `/chat` booking graph path.
- The graph relies on LLM-structured intent extraction; ensure API keys are valid before testing.

## Future Enhancements

- Replace mock hotel list with real inventory service/API.
- Persist confirmed bookings to a transactional database.
- Connect vector search tools into the active graph path where relevant.
- Add tests for graph transitions and schema edge cases.
