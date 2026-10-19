import io
from fastapi import status
from fastapi.testclient import TestClient

def test_create_product_success(client: TestClient, auth_headers: dict[str, str]):
    """Verifica que un usuario autenticado pueda crear un producto."""
    product_data = {
        "title": "MacBook Pro M3",
        "description": "Laptop de alto rendimiento",
        "price": 1999.99,
        "stock": 10,
    }
    response = client.post("/products", json=product_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == product_data["title"]
    assert float(data["price"]) == product_data["price"]
    assert data["stock"] == product_data["stock"]
    assert "id" in data

def test_create_product_unauthorized(client: TestClient):
    """Verifica que no se permita crear un producto sin token JWT."""
    product_data = {
        "title": "Producto Anónimo",
        "price": 50.0,
        "stock": 5,
    }
    response = client.post("/products", json=product_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_list_products(client: TestClient, auth_headers: dict[str, str]):
    """Verifica el listado paginado de productos."""
    client.post(
        "/products",
        json={"title": "Item 1", "price": 10.0, "stock": 2},
        headers=auth_headers,
    )
    client.post(
        "/products",
        json={"title": "Item 2", "price": 20.0, "stock": 4},
        headers=auth_headers,
    )

    response = client.get("/products?skip=0&limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_get_product_by_id(client: TestClient, auth_headers: dict[str, str]):
    """Verifica la consulta de un producto por ID."""
    created = client.post(
        "/products",
        json={"title": "Teclado Mecánico", "price": 89.99, "stock": 15},
        headers=auth_headers,
    ).json()

    response = client.get(f"/products/{created['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Teclado Mecánico"

def test_get_product_not_found(client: TestClient):
    """Verifica 404 al consultar un ID que no existe."""
    response = client.get("/products/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_upload_product_image_success(client: TestClient, auth_headers: dict[str, str]):
    """Verifica la subida de imagen a S3 asociada al producto."""
    created = client.post(
        "/products",
        json={"title": "Mouse Gamer", "price": 45.0, "stock": 8},
        headers=auth_headers,
    ).json()

    # Archivo simulado en memoria
    file_content = b"fake-jpeg-image-bytes"
    files = {"file": ("mouse.jpg", io.BytesIO(file_content), "image/jpeg")}

    response = client.post(
        f"/products/{created['id']}/image",
        files=files,
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert "image_url" in response.json()
    assert response.json()["image_url"] is not None

def test_upload_product_image_invalid_type(client: TestClient, auth_headers: dict[str, str]):
    """Verifica el rechazo de archivos que no cumplan los tipos MIME permitidos."""
    created = client.post(
        "/products",
        json={"title": "Monitor 4K", "price": 350.0, "stock": 3},
        headers=auth_headers,
    ).json()

    files = {"file": ("malicious.exe", io.BytesIO(b"binary-content"), "application/octet-stream")}

    response = client.post(
        f"/products/{created['id']}/image",
        files=files,
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Formato no permitido" in response.json()["detail"]

def test_update_product_forbidden_for_non_owner(client: TestClient, auth_headers: dict[str, str]):
    """Verifica que un usuario no pueda actualizar el producto de otro usuario."""
    # Crear producto con el primer usuario
    created = client.post(
        "/products",
        json={"title": "Silla Ergonómica", "price": 250.0, "stock": 5},
        headers=auth_headers,
    ).json()

    # Registrar e iniciar sesión con un segundo usuario
    client.post("/auth/register", json={
        "email": "user2@example.com",
        "username": "user2",
        "password": "Password123!",
    })
    token_user2 = client.post(
        "/auth/login",
        data={"username": "user2@example.com", "password": "Password123!"},
    ).json()["access_token"]
    headers_user2 = {"Authorization": f"Bearer {token_user2}"}

    # Intentar actualizar con el segundo usuario
    response = client.put(
        f"/products/{created['id']}",
        json={"price": 199.99},
        headers=headers_user2,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_product_success(client: TestClient, auth_headers: dict[str, str]):
    """Verifica que el propietario pueda eliminar su producto."""
    created = client.post(
        "/products",
        json={"title": "Producto a Borrar", "price": 15.0, "stock": 1},
        headers=auth_headers,
    ).json()

    delete_resp = client.delete(f"/products/{created['id']}", headers=auth_headers)
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

    # Verificar que ya no existe
    get_resp = client.get(f"/products/{created['id']}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
