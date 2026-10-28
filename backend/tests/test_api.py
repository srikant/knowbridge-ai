from fastapi.testclient import TestClient
from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["docs"] == "/docs"


def test_upload_and_ask(tmp_path, monkeypatch):
    from app import config
    monkeypatch.setattr(config, "LLM_PROVIDER", "none")
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    monkeypatch.setattr(config, "OLLAMA_ENABLED", False)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    # Rebind the DB path used by the database module too.
    from app import database
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    with TestClient(app) as client:
        upload = client.post("/api/documents", files={"file": ("policy.txt", b"Employees can request annual leave through the HR portal. Managers approve leave requests.", "text/plain")})
        assert upload.status_code == 201
        result = client.post("/api/ask", json={"question": "How do employees request annual leave?"})
        assert result.status_code == 200
        assert result.json()["sources"]


def test_delete_document(tmp_path, monkeypatch):
    from app import database
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "delete-test.db")
    with TestClient(app) as client:
        upload = client.post("/api/documents", files={"file": ("delete-me.txt", b"A short document about engineering practices.", "text/plain")})
        assert upload.status_code == 201
        document_id = upload.json()["id"]
        deleted = client.delete(f"/api/documents/{document_id}")
        assert deleted.status_code == 204
        listed = client.get("/api/documents")
        assert all(doc["id"] != document_id for doc in listed.json())


def test_integrations_endpoint_does_not_expose_secrets():
    with TestClient(app) as client:
        response = client.get("/api/integrations")
        assert response.status_code == 200
        body = response.json()
        assert "llm" in body
        assert "vector_store" in body
        assert "orchestration" in body
        assert "observability" in body
        assert "evaluation" in body
        assert "OPENAI_API_KEY" not in response.text


def test_provider_selection_prefers_openai_when_auto(monkeypatch):
    from app import config
    from app.services.llm import selected_provider

    monkeypatch.setattr(config, "LLM_PROVIDER", "auto")
    monkeypatch.setattr(config, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(config, "OLLAMA_ENABLED", True)
    assert selected_provider() == "openai"


def test_provider_selection_can_use_ollama(monkeypatch):
    from app import config
    from app.services.llm import selected_provider

    monkeypatch.setattr(config, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    monkeypatch.setattr(config, "OLLAMA_ENABLED", True)
    assert selected_provider() == "ollama"


def test_provider_selection_falls_back_to_retrieval(monkeypatch):
    from app import config
    from app.services.llm import selected_provider

    monkeypatch.setattr(config, "LLM_PROVIDER", "auto")
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    monkeypatch.setattr(config, "OLLAMA_ENABLED", False)
    assert selected_provider() == "none"
