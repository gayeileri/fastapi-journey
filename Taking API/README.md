Database migration notes:

- A `password_hash` column was added to the `User` model. To apply this change to your database run the SQL in `migrations/add_password_hash.sql` against your Postgres database, for example:

```bash
psql $DATABASE_URL -f migrations/add_password_hash.sql
```

Or create an Alembic revision and apply it if you use Alembic.
## Project Structure
- `app/models/`: SQLAlchemy database models
- `app/schemas/`: Pydantic validation schemas
- `app/routes/`: API endpoints
- `app/services/`: Core logic (Markdown, OpenAI, Grammar)
- `app/tasks/`: Background tasks (AI Summary generation)
- `app/utils/`: Helpers (File validation, Text extraction)
# Brief 20: Markdown Note-Taking API (Phase 2)

A production-ready FastAPI backend for creating, rendering, and managing Markdown notes.

## Features
- CRUD operations for Notes
- Markdown to HTML conversion with Redis Caching
- Note versioning (keeps history of changes)
- Many-to-many tag system
- AI-powered summary and tag generation via OpenAI API
- Grammar checking via LanguageTool
- Markdown file upload with validation

## Requirements
- Python 3.9+
- PostgreSQL
- Redis
- Docker (optional, for running DBs)

## Setup Instructions

1. **Clone and Setup Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```

3. **Database Setup (Docker Method):**
   ```bash
   docker run -d --name postgres_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=notes_db -p 5432:5432 postgres
   docker run -d --name redis_db -p 6379:6379 redis
   ```

4. **Run the API:**
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation
Once the server is running, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`
- Frontend Demo: `http://127.0.0.1:8000/`

## Project Structure
- `app/models/`: SQLAlchemy database models
- `app/schemas/`: Pydantic validation schemas
- `app/routes/`: API endpoints
- `app/services/`: Core logic (Markdown, OpenAI, Grammar)
- `app/tasks/`: Background tasks (AI Summary generation)
- `app/utils/`: Helpers (File validation, Text extraction)
