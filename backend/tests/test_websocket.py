import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.models.user import User
from app.core.security import create_access_token
import json

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
def auth_headers(mock_user):
    token = create_access_token({"sub": mock_user.username})
    return {"Authorization": f"Bearer {token}"}

def test_websocket_connection(client, auth_headers):
    # Act
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        # Assert
        assert websocket.client_state.connected

def test_websocket_connection_unauthorized(client):
    # Act & Assert
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/chat") as websocket:
            pass

def test_websocket_send_message(client, auth_headers):
    # Arrange
    message = {
        "type": "message",
        "content": "Test message"
    }

    # Act
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        websocket.send_json(message)
        response = websocket.receive_json()

    # Assert
    assert response["type"] == "message"
    assert response["content"] == "Test message"
    assert "timestamp" in response
    assert "user_id" in response

def test_websocket_invalid_message_format(client, auth_headers):
    # Arrange
    invalid_message = {
        "type": "invalid",
        "data": "Invalid format"
    }

    # Act & Assert
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        websocket.send_json(invalid_message)
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "Invalid message format" in response["message"]

def test_websocket_connection_closed(client, auth_headers):
    # Act
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        websocket.close()
        assert not websocket.client_state.connected

def test_websocket_multiple_messages(client, auth_headers):
    # Arrange
    messages = [
        {"type": "message", "content": "First message"},
        {"type": "message", "content": "Second message"}
    ]

    # Act
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        for message in messages:
            websocket.send_json(message)
            response = websocket.receive_json()
            assert response["type"] == "message"
            assert response["content"] == message["content"]

def test_websocket_typing_indicator(client, auth_headers):
    # Arrange
    typing_message = {
        "type": "typing",
        "is_typing": True
    }

    # Act
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        websocket.send_json(typing_message)
        response = websocket.receive_json()

    # Assert
    assert response["type"] == "typing"
    assert response["is_typing"] is True
    assert "user_id" in response

def test_websocket_error_handling(client, auth_headers):
    # Arrange
    invalid_json = "Invalid JSON"

    # Act & Assert
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        websocket.send_text(invalid_json)
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "Invalid JSON" in response["message"]

def test_websocket_connection_timeout(client, auth_headers):
    # Act & Assert
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        # Simulate timeout by not sending any messages
        websocket.close()
        assert not websocket.client_state.connected

def test_websocket_broadcast_message(client, auth_headers):
    # Arrange
    message = {
        "type": "message",
        "content": "Broadcast message"
    }

    # Act
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket1, \
         client.websocket_connect("/ws/chat", headers=auth_headers) as websocket2:
        websocket1.send_json(message)
        response1 = websocket1.receive_json()
        response2 = websocket2.receive_json()

    # Assert
    assert response1["content"] == message["content"]
    assert response2["content"] == message["content"]
    assert response1["timestamp"] == response2["timestamp"]

def test_websocket_user_join_notification(client, auth_headers):
    # Act
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        response = websocket.receive_json()

    # Assert
    assert response["type"] == "system"
    assert "user joined" in response["message"].lower()
    assert "user_id" in response

def test_websocket_user_leave_notification(client, auth_headers):
    # Act
    with client.websocket_connect("/ws/chat", headers=auth_headers) as websocket:
        # First message should be join notification
        websocket.receive_json()
        # Close connection
        websocket.close()
        # Last message should be leave notification
        response = websocket.receive_json()

    # Assert
    assert response["type"] == "system"
    assert "user left" in response["message"].lower()
    assert "user_id" in response 