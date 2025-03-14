import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.models.user import User
from app.models.document import Document
from app.models.chat import ChatMessage
from app.core.security import create_access_token

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )

@pytest.fixture
def mock_document():
    return Document(
        id=1,
        user_id=1,
        filename="test.pdf",
        content="Test document content",
        embedding=[0.1, 0.2, 0.3]
    )

@pytest.fixture
def mock_chat_message():
    return ChatMessage(
        id=1,
        user_id=1,
        content="Test message",
        is_user=True
    )

@pytest.fixture
def auth_headers(mock_user):
    token = create_access_token({"sub": mock_user.username})
    return {"Authorization": f"Bearer {token}"}

def test_register_user(client):
    # Arrange
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "testpass123",
        "full_name": "New User"
    }

    # Act
    response = client.post("/api/auth/register", json=user_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data

def test_register_user_duplicate_username(client, mock_user):
    # Arrange
    user_data = {
        "username": mock_user.username,
        "email": "different@example.com",
        "password": "testpass123",
        "full_name": "New User"
    }

    # Act
    response = client.post("/api/auth/register", json=user_data)

    # Assert
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_login_user(client, mock_user):
    # Arrange
    login_data = {
        "username": mock_user.username,
        "password": "testpass123"
    }

    # Act
    response = client.post("/api/auth/login", data=login_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_invalid_credentials(client, mock_user):
    # Arrange
    login_data = {
        "username": mock_user.username,
        "password": "wrongpass"
    }

    # Act
    response = client.post("/api/auth/login", data=login_data)

    # Assert
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_get_current_user(client, mock_user, auth_headers):
    # Act
    response = client.get("/api/auth/me", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == mock_user.username
    assert data["email"] == mock_user.email
    assert data["full_name"] == mock_user.full_name

def test_get_current_user_invalid_token(client):
    # Arrange
    headers = {"Authorization": "Bearer invalid.token.string"}

    # Act
    response = client.get("/api/auth/me", headers=headers)

    # Assert
    assert response.status_code == 401

def test_upload_document(client, mock_document, auth_headers):
    # Arrange
    files = {
        "file": ("test.pdf", b"Test document content", "application/pdf")
    }

    # Act
    response = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files=files
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == mock_document.filename
    assert data["content"] == mock_document.content
    assert "id" in data
    assert "user_id" in data

def test_get_user_documents(client, mock_document, auth_headers):
    # Act
    response = client.get("/api/documents", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["filename"] == mock_document.filename
    assert data[0]["content"] == mock_document.content

def test_delete_document(client, mock_document, auth_headers):
    # Act
    response = client.delete(
        f"/api/documents/{mock_document.id}",
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 204

def test_delete_document_not_found(client, auth_headers):
    # Act
    response = client.delete(
        "/api/documents/999",
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 404

def test_send_chat_message(client, mock_chat_message, auth_headers):
    # Arrange
    message_data = {
        "content": "Test message"
    }

    # Act
    response = client.post(
        "/api/chat/message",
        headers=auth_headers,
        json=message_data
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == message_data["content"]
    assert data["is_user"] is True
    assert "id" in data
    assert "user_id" in data

def test_get_chat_history(client, mock_chat_message, auth_headers):
    # Act
    response = client.get("/api/chat/history", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["content"] == mock_chat_message.content
    assert data[0]["is_user"] == mock_chat_message.is_user

def test_clear_chat_history(client, auth_headers):
    # Act
    response = client.delete("/api/chat/history", headers=auth_headers)

    # Assert
    assert response.status_code == 204

def test_unauthorized_access(client):
    # Act
    response = client.get("/api/documents")

    # Assert
    assert response.status_code == 401 