from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import notes
from app.core.database import engine, Base
from app.core.ratelimit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.routes import auth as auth_routes
import os

# Create tables (best-effort). If the DB is unavailable during development, log and continue.
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    import logging
    logging.getLogger(__name__).warning("Could not create DB tables at startup: %s", e)

app = FastAPI(title="Markdown Note-Taking API", version="1.0.0")

# Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(auth_routes.router)
app.include_router(notes.router)

# Mount static files for frontend demo
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")
@app.get("/health")
def health():
    return {"status": "ok"}