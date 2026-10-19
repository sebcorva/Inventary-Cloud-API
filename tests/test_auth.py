from fastapi import status
from fastapi.testclient import TestClient

def test_register_user_success(client: TestClient):
    """Verifica que un usuario nuevo se registre correctamente."""
    payload = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "Password123!",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "id" in data
    assert "password" not in data

def test_register_duplicate_email(client: TestClient):
    """Verifica que no se permita registrar el mismo email dos veces."""
    payload = {
        "email": "dup@example.com",
        "username": "userone",
        "password": "Password123!",
    }
    client.post("/auth/register", json=payload)

    dup_payload = {
        "email": "dup@example.com",
        "username": "usertwo",
        "password": "Password123!",
    }
    response = client.post("/auth/register", json=dup_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "correo electronico ya esta registrado" in response.json()["detail"]

def test_register_duplicate_username(client: TestClient):
    """Verifica que no se permita registrar el mismo username dos veces."""
    payload = {
        "email": "unique1@example.com",
        "username": "sameuser",
        "password": "Password123!",
    }
    client.post("/auth/register", json=payload)

    dup_payload = {
        "email": "unique2@example.com",
        "username": "sameuser",
        "password": "Password123!",
    }
    response = client.post("/auth/register", json=dup_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "nombre de usuario ya existe" in response.json()["detail"]

def test_login_success(client: TestClient):
    """Verifica inicio de sesión exitoso y entrega de token JWT."""
    user_payload = {
        "email": "loginuser@example.com",
        "username": "loginuser",
        "password": "Password123!",
    }
    client.post("/auth/register", json=user_payload)

    response = client.post(
        "/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"

def test_login_invalid_password(client: TestClient):
    """Verifica rechazo de login con contraseña incorrecta."""
    user_payload = {
        "email": "badpass@example.com",
        "username": "badpass",
        "password": "Password123!",
    }
    client.post("/auth/register", json=user_payload)

    response = client.post(
        "/auth/login",
        data={"username": user_payload["email"], "password": "WrongPassword!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
