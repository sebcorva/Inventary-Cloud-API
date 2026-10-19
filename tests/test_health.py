from fastapi import status
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Verifica que el endpoint de healthcheck responda 200 y el estado esperado."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "service" in data
