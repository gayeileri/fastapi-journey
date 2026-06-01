from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from app.core import security


def key_func(request: Request) -> str:
    """
    Key function that prefers an authenticated user's username (from Bearer token)
    and falls back to the remote IP address for unauthenticated requests.
    This allows per-user rate limits while still limiting anonymous traffic.
    """
    auth: str = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = security.decode_token(token)
            sub = payload.get("sub")
            if sub:
                return f"user:{sub}"
        except Exception:
            # If token invalid, fall back to IP-based key
            pass
    return get_remote_address(request)


# Limiter instance to import in routes
limiter = Limiter(key_func=key_func)
