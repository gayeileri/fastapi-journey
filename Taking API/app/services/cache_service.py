from app.core.redis import redis_client

def get_rendered_html(note_id: int) -> str:
    return redis_client.get(f"rendered_note:{note_id}")

def cache_rendered_html(note_id: int, html_content: str):
    redis_client.set(f"rendered_note:{note_id}", html_content)

def invalidate_cache(note_id: int):
    redis_client.delete(f"rendered_note:{note_id}")
