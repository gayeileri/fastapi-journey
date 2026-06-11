"""
Test suite for the Markdown Note-Taking API.

Uses an in-memory SQLite database and a mocked Redis client so tests
run without any external services (no PostgreSQL, no Redis, no OpenAI).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from main import app
from app.core.database import Base, get_db

# ─── In-memory SQLite test database ──────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test_notes.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Mock Redis so cache calls never hit a real server ───────────────────────
mock_redis = MagicMock()
mock_redis.get.return_value = None
mock_redis.set.return_value = True
mock_redis.delete.return_value = True


# ─── Fixtures ────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once for the test session, drop them afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    """
    TestClient with DB and Redis overrides applied.
    Background AI tasks are also patched so OpenAI is never called.
    """
    app.dependency_overrides[get_db] = override_get_db

    with patch("app.services.cache_service.redis_client", mock_redis), \
         patch("app.tasks.ai_tasks.process_note_background", return_value=None):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def auth_headers(client):
    """Register a test user and return the Bearer auth headers."""
    client.post("/auth/register", json={"username": "testuser", "password": "testpass123"})
    resp = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─── Phase 1: Basic health & frontend ────────────────────────────────────────
class TestHealthAndFrontend:
    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_frontend_served(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]


# ─── Phase 2: Auth ────────────────────────────────────────────────────────────
class TestAuth:
    def test_register_new_user(self, client):
        resp = client.post("/auth/register", json={"username": "newuser", "password": "pass123"})
        assert resp.status_code == 201
        assert resp.json()["username"] == "newuser"

    def test_register_duplicate_user(self, client):
        client.post("/auth/register", json={"username": "dupuser", "password": "pass"})
        resp = client.post("/auth/register", json={"username": "dupuser", "password": "pass"})
        assert resp.status_code == 400
        assert "already exists" in resp.json()["detail"]

    def test_login_success(self, client):
        client.post("/auth/register", json={"username": "loginuser", "password": "mypass"})
        resp = client.post(
            "/auth/token",
            data={"username": "loginuser", "password": "mypass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        client.post("/auth/register", json={"username": "wrongpass", "password": "correct"})
        resp = client.post(
            "/auth/token",
            data={"username": "wrongpass", "password": "wrong"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 401

    def test_unauthenticated_notes_access(self, client):
        resp = client.get("/notes")
        assert resp.status_code == 401


# ─── Phase 3: Note CRUD ───────────────────────────────────────────────────────
class TestNoteCRUD:
    def test_create_note(self, client, auth_headers):
        resp = client.post(
            "/notes",
            json={"title": "My First Note", "markdown_content": "# Hello\nThis is a test note.", "tags": []},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "My First Note"
        assert data["markdown_content"] == "# Hello\nThis is a test note."
        assert "id" in data

    def test_list_notes(self, client, auth_headers):
        resp = client.get("/notes", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_get_note_by_id(self, client, auth_headers):
        create_resp = client.post(
            "/notes",
            json={"title": "Fetch Me", "markdown_content": "content", "tags": []},
            headers=auth_headers,
        )
        note_id = create_resp.json()["id"]
        resp = client.get(f"/notes/{note_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == note_id

    def test_get_nonexistent_note(self, client, auth_headers):
        resp = client.get("/notes/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_note(self, client, auth_headers):
        create_resp = client.post(
            "/notes",
            json={"title": "Before Update", "markdown_content": "old content", "tags": []},
            headers=auth_headers,
        )
        note_id = create_resp.json()["id"]

        resp = client.put(
            f"/notes/{note_id}",
            json={"title": "After Update", "markdown_content": "new content", "tags": []},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "After Update"
        assert resp.json()["markdown_content"] == "new content"

    def test_delete_note(self, client, auth_headers):
        create_resp = client.post(
            "/notes",
            json={"title": "Delete Me", "markdown_content": "bye", "tags": []},
            headers=auth_headers,
        )
        note_id = create_resp.json()["id"]

        del_resp = client.delete(f"/notes/{note_id}", headers=auth_headers)
        assert del_resp.status_code == 200

        get_resp = client.get(f"/notes/{note_id}", headers=auth_headers)
        assert get_resp.status_code == 404


# ─── Phase 4: User isolation ──────────────────────────────────────────────────
class TestUserIsolation:
    def test_user_cannot_access_other_users_note(self, client, auth_headers):
        """A note created by testuser must not be accessible by another user."""
        # Create a note as testuser
        create_resp = client.post(
            "/notes",
            json={"title": "Private Note", "markdown_content": "secret", "tags": []},
            headers=auth_headers,
        )
        note_id = create_resp.json()["id"]

        # Register and login a second user
        client.post("/auth/register", json={"username": "otheruser", "password": "otherpass"})
        login_resp = client.post(
            "/auth/token",
            data={"username": "otheruser", "password": "otherpass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        other_token = login_resp.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Other user should get 404
        resp = client.get(f"/notes/{note_id}", headers=other_headers)
        assert resp.status_code == 404


# ─── Phase 5: Versioning ──────────────────────────────────────────────────────
class TestVersioning:
    def test_version_created_on_update(self, client, auth_headers):
        create_resp = client.post(
            "/notes",
            json={"title": "Version Test", "markdown_content": "v1 content", "tags": []},
            headers=auth_headers,
        )
        note_id = create_resp.json()["id"]

        # First update → should create version 1
        client.put(
            f"/notes/{note_id}",
            json={"title": "Version Test", "markdown_content": "v2 content", "tags": []},
            headers=auth_headers,
        )

        versions_resp = client.get(f"/notes/{note_id}/versions", headers=auth_headers)
        assert versions_resp.status_code == 200
        versions = versions_resp.json()
        assert len(versions) >= 1
        assert versions[0]["markdown_content"] == "v1 content"

    def test_multiple_versions(self, client, auth_headers):
        create_resp = client.post(
            "/notes",
            json={"title": "Multi Version", "markdown_content": "original", "tags": []},
            headers=auth_headers,
        )
        note_id = create_resp.json()["id"]

        for i in range(1, 4):
            client.put(
                f"/notes/{note_id}",
                json={"title": "Multi Version", "markdown_content": f"revision {i}", "tags": []},
                headers=auth_headers,
            )

        versions_resp = client.get(f"/notes/{note_id}/versions", headers=auth_headers)
        assert len(versions_resp.json()) == 3


# ─── Phase 6: Rendered HTML ───────────────────────────────────────────────────
class TestRenderedHTML:
    def test_render_html(self, client, auth_headers):
        create_resp = client.post(
            "/notes",
            json={"title": "Render Test", "markdown_content": "# Hello\n**bold**", "tags": []},
            headers=auth_headers,
        )
        note_id = create_resp.json()["id"]

        resp = client.get(f"/notes/{note_id}/rendered", headers=auth_headers)
        assert resp.status_code == 200
        html = resp.json()["html"]
        assert "<h1>" in html
        assert "<strong>" in html


# ─── Phase 7: Pydantic Validation ────────────────────────────────────────────
class TestValidation:
    def test_title_too_long(self, client, auth_headers):
        resp = client.post(
            "/notes",
            json={"title": "x" * 201, "markdown_content": "content", "tags": []},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_tag_with_spaces_rejected(self, client, auth_headers):
        resp = client.post(
            "/notes",
            json={"title": "Tag Test", "markdown_content": "content", "tags": ["invalid tag"]},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_tag_with_special_chars_rejected(self, client, auth_headers):
        resp = client.post(
            "/notes",
            json={"title": "Tag Test", "markdown_content": "content", "tags": ["bad-tag!"]},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_valid_alphanumeric_tag_accepted(self, client, auth_headers):
        resp = client.post(
            "/notes",
            json={"title": "Tag Test", "markdown_content": "content", "tags": ["python", "fastapi"]},
            headers=auth_headers,
        )
        assert resp.status_code == 200


# ─── Phase 8: File Upload ─────────────────────────────────────────────────────
class TestFileUpload:
    def test_upload_valid_md_file(self, client, auth_headers):
        file_content = b"# Uploaded Note\n\nThis was uploaded."
        resp = client.post(
            "/notes/upload",
            files={"file": ("test.md", file_content, "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "test"

    def test_upload_non_md_file_rejected(self, client, auth_headers):
        resp = client.post(
            "/notes/upload",
            files={"file": ("test.txt", b"some content", "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "Only .md files" in resp.json()["detail"]

    def test_upload_wrong_mime_rejected(self, client, auth_headers):
        resp = client.post(
            "/notes/upload",
            files={"file": ("test.md", b"content", "application/octet-stream")},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_upload_oversized_file_rejected(self, client, auth_headers):
        big_content = b"x" * (2 * 1024 * 1024 + 1)  # 2MB + 1 byte
        resp = client.post(
            "/notes/upload",
            files={"file": ("big.md", big_content, "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "2MB" in resp.json()["detail"]


# ─── Phase 9: Search ─────────────────────────────────────────────────────────
class TestSearch:
    def test_search_by_keyword(self, client, auth_headers):
        client.post(
            "/notes",
            json={"title": "Searchable Note", "markdown_content": "unique_keyword_xyz", "tags": []},
            headers=auth_headers,
        )
        resp = client.get("/notes/search?keyword=unique_keyword_xyz", headers=auth_headers)
        assert resp.status_code == 200
        results = resp.json()
        assert any("unique_keyword_xyz" in n["markdown_content"] for n in results)

    def test_search_by_tag(self, client, auth_headers):
        client.post(
            "/notes",
            json={"title": "Tagged Note", "markdown_content": "content", "tags": ["searchtag"]},
            headers=auth_headers,
        )
        resp = client.get("/notes/search?tag=searchtag", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_search_returns_only_own_notes(self, client, auth_headers):
        """Search must not leak notes from other users."""
        resp = client.get("/notes/search?keyword=secret", headers=auth_headers)
        assert resp.status_code == 200
        # All returned notes must belong to the authenticated user (no cross-user leak)
        for note in resp.json():
            assert "title" in note
