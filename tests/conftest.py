from collections.abc import Generator
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.services.s3_service import s3_service
from app.services.sqs_service import sqs_service

# Base de datos SQLite en memoria para tests aislados 
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Crea las tablas en la base de datos de test y las limpia al finalizar."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Proporciona una sesión de base de datos aislada con rollback al finalizar cada test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Cliente HTTP de pruebas con la dependencia get_db sobreescrita."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_aws_services():
    """Simula las llamadas a AWS S3 y SQS para no depender de la nube en los tests."""
    with patch.object(
        s3_service,
        "upload_file",
        return_value="https://test-bucket.s3.us-east-1.amazonaws.com/products/test-image.jpg",
    ), patch.object(
        s3_service,
        "delete_file_by_url",
        return_value=True,
    ), patch.object(
        sqs_service,
        "send_event",
        return_value="mocked-sqs-message-id-123",
    ):
        yield

@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Registra y autentica un usuario de prueba, retornando los headers de autorización Bearer."""
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "SecretPassword123!",
    }
    # Registrar usuario
    client.post("/auth/register", json=user_data)

    # Iniciar sesión para obtener el token JWT
    login_response = client.post(
        "/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
