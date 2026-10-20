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


def test_correlation_id_middleware(client: TestClient):
    """Verifica que el middleware inyecte X-Request-ID y X-Process-Time."""
    # 1. Sin header previo (debe auto-generar uno)
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers
    assert len(response.headers["x-request-id"]) > 0

    # 2. Con header personalizado enviado por el cliente/ALB (debe preservarlo)
    custom_trace_id = "alb-trace-uuid-98765"
    response_custom = client.get("/health", headers={"X-Request-ID": custom_trace_id})
    assert response_custom.status_code == status.HTTP_200_OK
    assert response_custom.headers.get("x-request-id") == custom_trace_id

