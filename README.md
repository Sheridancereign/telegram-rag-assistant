# Telegram RAG Assistant

A Telegram bot that answers questions about your documents using Retrieval-Augmented Generation (RAG). Upload a PDF or
TXT file, then ask questions about its content — the bot finds relevant passages via semantic vector search and
generates grounded answers using Google Gemini.

## How it works

1. **Ingestion** — user sends a document → text is extracted and split into overlapping chunks → each chunk is embedded
   into a 768-dimensional vector via Gemini Embeddings → chunks and vectors are stored in PostgreSQL
2. **Retrieval** — user asks a question → the question is embedded the same way → PostgreSQL (via `pgvector` + HNSW
   index) finds the most semantically similar chunks using cosine distance
3. **Generation** — the retrieved chunks are injected into a prompt as context → Gemini generates an answer grounded in
   the actual document, not general knowledge

## Tech stack

| Component             | Technology                                      |
|-----------------------|-------------------------------------------------|
| Language & runtime    | Python 3.12+, asyncio                           |
| Telegram interface    | aiogram 3.x                                     |
| LLM provider          | Google Gemini API (`google-genai` SDK)          |
| Embeddings            | `gemini-embedding-001` (768-dim, L2-normalized) |
| Generation            | `gemini-3.6-flash`                              |
| Vector database       | PostgreSQL 16 + `pgvector` (HNSW, cosine ops)   |
| ORM / DB driver       | SQLAlchemy 2.0 (async) + asyncpg                |
| Migrations            | Alembic                                         |
| Document parsing      | pypdf                                           |
| Dependency management | Poetry                                          |
| Testing               | pytest, pytest-asyncio                          |
| Infrastructure        | Docker Compose                                  |

## Project structure

app/
├── main.py # Entry point, aiogram bot startup
├── config.py # Settings via pydantic-settings
├── bot/
│ ├── handlers/ # /start, document upload, question handling
│ ├── middlewares/ # DB session middleware
│ └── states.py # FSM states
├── core/
│ ├── chunker.py # Text splitting
│ ├── embeddings.py # Gemini embeddings wrapper
│ └── rag_engine.py # Prompt building + answer generation
└── db/
├── base.py # Async engine & session factory
├── models.py # SQLAlchemy models (User, Document, DocumentChunk)
└── repository.py # Async CRUD + vector search

migrations/ # Alembic migrations
tests/ # Unit + integration tests



## Database schema

Three tables: `users`, `documents`, `document_chunks`. The key column is `document_chunks.embedding`, a `vector(768)` column indexed with HNSW for fast approximate cosine-similarity search:

```sql
CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops);
```

## Getting started

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker & Docker Compose
- A Telegram bot token ([@BotFather](https://t.me/BotFather))
- A Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

### Setup

```bash
git clone https://github.com/Sheridancereign/telegram-rag-assistant.git
cd telegram-rag-assistant

poetry install

cp .env.example .env
# fill in BOT_TOKEN and GEMINI_API_KEY in .env

docker compose up -d

poetry run alembic upgrade head

poetry run python -m app.main
```

### Running tests

```bash
poetry run pytest -v
```

Unit tests (chunker, embeddings, rag_engine) run in isolation with mocked API calls. Integration tests (repository) run against a real PostgreSQL instance, with each test wrapped in a transaction that's rolled back afterward.

## Status

🚧 Personal project, actively developed.