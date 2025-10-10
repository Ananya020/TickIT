import os
os.environ["SKIP_AUTH"] = "true"
r = client.post("/api/chat", json={"query": "How many open tickets?"})

import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure the app uses SKIP_AI_INIT to avoid external calls in tests
os.environ["SKIP_AI_INIT"] = "true"

# Force an in-repo SQLite DB for tests so we don't require external DB drivers
os.environ["DATABASE_URL"] = "sqlite:///./test_tickit.db"

# Add workspace root to sys.path so we can import package 'backend'
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.main import app

client = TestClient(app)


def test_chat_health():
    r = client.get("/api/chat/health")
    assert r.status_code == 200
    body = r.json()
    assert "status" in body


def test_chat_post_mocked():
    # When SKIP_AI_INIT=true the chat endpoint should return a fallback response
    r = client.post("/api/chat", json={"query": "How many open tickets?"})
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert isinstance(data["response"], str)
