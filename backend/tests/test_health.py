from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    # Should serve either HTML homepage or JSON API status
    assert "ExamPilote" in response.text

def test_platform_health_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_api_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["name"] == "ExamPilote API"

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ExamPilote API"

def test_database_health_endpoint():
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "masked_uri" in data
    assert "details" in data
    # Ensure sensitive credentials are never exposed
    assert "@cluster1" in data["masked_uri"] or "bumblebee" in data["masked_uri"] or "mongodb" in data["masked_uri"]
    assert ":***@" in data["masked_uri"] or "@" not in data["masked_uri"]
