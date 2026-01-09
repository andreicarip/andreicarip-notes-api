import uuid
import os
import sys
from fastapi.testclient import TestClient

# Make sure /opt/api (project root) is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from main import app

client = TestClient(app)


def test_health_endpoint():
    """Basic health check should return status=ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert data.get("status") == "ok"


def test_full_notes_flow():
    """
    End-to-end test:
    - register a new user with a unique username
    - login and get JWT
    - create a note
    - list notes and see the note
    - delete the note
    """

    # Make username unique every run so tests don't collide
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "test-password-123"

    # 1) Register
    reg_resp = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    assert reg_resp.status_code in (200, 201), reg_resp.text

    # 2) Login (FastAPI OAuth2PasswordRequestForm uses form-encoded body)
    login_resp = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert login_resp.status_code == 200, login_resp.text
    login_data = login_resp.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3) Create a note
    note_payload = {"title": "Test note", "content": "This is a test note from pytest."}
    create_resp = client.post("/notes", json=note_payload, headers=headers)
    assert create_resp.status_code in (200, 201), create_resp.text
    created_note = create_resp.json()
    assert created_note.get("title") == note_payload["title"]
    assert created_note.get("content") == note_payload["content"]
    note_id = created_note.get("id")

    # 4) List notes and ensure the new one is present
    list_resp = client.get("/notes", headers=headers)
    assert list_resp.status_code == 200, list_resp.text
    notes = list_resp.json()
    assert isinstance(notes, list)
    assert any(n.get("id") == note_id for n in notes)

    # 5) Delete the note
    delete_resp = client.delete(f"/notes/{note_id}", headers=headers)
    assert delete_resp.status_code in (200, 204), delete_resp.text
