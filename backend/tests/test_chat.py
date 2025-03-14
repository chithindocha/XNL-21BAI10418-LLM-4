import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.chat import ChatService
from app.models.chat import ChatMessage
from app.models.user import User
from app.models.document import Document
from app.core.config import settings

@pytest.fixture
def mock_db():
    return Mock(spec=Session)

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
def chat_service(mock_db):
    return ChatService(mock_db)

def test_create_chat_message(chat_service, mock_user):
    # Arrange
    content = "Test message"
    chat_service.db.add = Mock()
    chat_service.db.commit = Mock()
    chat_service.db.refresh = Mock()

    # Act
    message = chat_service.create_chat_message(
        user_id=mock_user.id,
        content=content,
        is_user=True
    )

    # Assert
    assert message.content == content
    assert message.user_id == mock_user.id
    assert message.is_user is True
    chat_service.db.add.assert_called_once()
    chat_service.db.commit.assert_called_once()
    chat_service.db.refresh.assert_called_once()

def test_get_chat_history(chat_service, mock_user):
    # Arrange
    mock_messages = [
        ChatMessage(id=1, user_id=mock_user.id, content="Hello", is_user=True),
        ChatMessage(id=2, user_id=mock_user.id, content="Hi there", is_user=False)
    ]
    chat_service.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_messages

    # Act
    messages = chat_service.get_chat_history(mock_user.id)

    # Assert
    assert len(messages) == 2
    assert messages[0].content == "Hello"
    assert messages[1].content == "Hi there"
    chat_service.db.query.assert_called_once_with(ChatMessage)

def test_get_relevant_context(chat_service, mock_user, mock_document):
    # Arrange
    mock_documents = [mock_document]
    chat_service.db.query.return_value.filter.return_value.all.return_value = mock_documents

    # Act
    context = chat_service.get_relevant_context(mock_user.id, "test query")

    # Assert
    assert context == "Test document content"
    chat_service.db.query.assert_called_once_with(Document)

def test_get_relevant_context_no_documents(chat_service, mock_user):
    # Arrange
    chat_service.db.query.return_value.filter.return_value.all.return_value = []

    # Act
    context = chat_service.get_relevant_context(mock_user.id, "test query")

    # Assert
    assert context == ""

@patch('app.services.chat.openai.ChatCompletion.create')
def test_get_chat_response(mock_openai, chat_service, mock_user):
    # Arrange
    mock_openai.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    chat_service.get_relevant_context = Mock(return_value="Test context")
    chat_service.create_chat_message = Mock()

    # Act
    response = chat_service.get_chat_response(mock_user.id, "test query")

    # Assert
    assert response == "Test response"
    mock_openai.assert_called_once()
    chat_service.get_relevant_context.assert_called_once_with(mock_user.id, "test query")
    chat_service.create_chat_message.assert_called()

@patch('app.services.chat.openai.ChatCompletion.create')
def test_get_chat_response_error(mock_openai, chat_service, mock_user):
    # Arrange
    mock_openai.side_effect = Exception("API Error")
    chat_service.get_relevant_context = Mock(return_value="Test context")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        chat_service.get_chat_response(mock_user.id, "test query")
    assert str(exc_info.value) == "API Error"

def test_clear_chat_history(chat_service, mock_user):
    # Arrange
    chat_service.db.query.return_value.filter.return_value.delete = Mock()
    chat_service.db.commit = Mock()

    # Act
    chat_service.clear_chat_history(mock_user.id)

    # Assert
    chat_service.db.query.assert_called_once_with(ChatMessage)
    chat_service.db.commit.assert_called_once() 