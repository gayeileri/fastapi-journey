import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    # Should return the frontend HTML
    assert "text/html" in response.headers["content-type"]

def test_unauthenticated_notes_access():
    response = client.get("/notes")
    # Should be rejected because no JWT token is provided
    assert response.status_code == 401
