import pytest
from unittest.mock import Mock, patch
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.services.document import DocumentService
from app.models.document import Document
from app.models.user import User
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
def document_service(mock_db):
    return DocumentService(mock_db)

def test_create_document(document_service, mock_user):
    # Arrange
    filename = "test.pdf"
    content = "Test document content"
    embedding = [0.1, 0.2, 0.3]
    document_service.db.add = Mock()
    document_service.db.commit = Mock()
    document_service.db.refresh = Mock()

    # Act
    document = document_service.create_document(
        user_id=mock_user.id,
        filename=filename,
        content=content,
        embedding=embedding
    )

    # Assert
    assert document.filename == filename
    assert document.content == content
    assert document.embedding == embedding
    assert document.user_id == mock_user.id
    document_service.db.add.assert_called_once()
    document_service.db.commit.assert_called_once()
    document_service.db.refresh.assert_called_once()

def test_get_document(document_service, mock_document):
    # Arrange
    document_service.db.query.return_value.filter.return_value.first.return_value = mock_document

    # Act
    document = document_service.get_document(mock_document.id)

    # Assert
    assert document.id == mock_document.id
    assert document.filename == mock_document.filename
    assert document.content == mock_document.content
    document_service.db.query.assert_called_once_with(Document)

def test_get_document_not_found(document_service):
    # Arrange
    document_service.db.query.return_value.filter.return_value.first.return_value = None

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        document_service.get_document(999)
    assert str(exc_info.value) == "Document not found"

def test_get_user_documents(document_service, mock_user, mock_document):
    # Arrange
    mock_documents = [mock_document]
    document_service.db.query.return_value.filter.return_value.all.return_value = mock_documents

    # Act
    documents = document_service.get_user_documents(mock_user.id)

    # Assert
    assert len(documents) == 1
    assert documents[0].id == mock_document.id
    assert documents[0].user_id == mock_user.id
    document_service.db.query.assert_called_once_with(Document)

def test_delete_document(document_service, mock_document):
    # Arrange
    document_service.db.query.return_value.filter.return_value.first.return_value = mock_document
    document_service.db.delete = Mock()
    document_service.db.commit = Mock()

    # Act
    document_service.delete_document(mock_document.id)

    # Assert
    document_service.db.delete.assert_called_once_with(mock_document)
    document_service.db.commit.assert_called_once()

def test_delete_document_not_found(document_service):
    # Arrange
    document_service.db.query.return_value.filter.return_value.first.return_value = None

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        document_service.delete_document(999)
    assert str(exc_info.value) == "Document not found"

@patch('app.services.document.openai.Embedding.create')
def test_generate_embedding(mock_openai, document_service):
    # Arrange
    mock_openai.return_value = {
        "data": [{"embedding": [0.1, 0.2, 0.3]}]
    }

    # Act
    embedding = document_service.generate_embedding("Test content")

    # Assert
    assert embedding == [0.1, 0.2, 0.3]
    mock_openai.assert_called_once()

@patch('app.services.document.openai.Embedding.create')
def test_generate_embedding_error(mock_openai, document_service):
    # Arrange
    mock_openai.side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        document_service.generate_embedding("Test content")
    assert str(exc_info.value) == "API Error"

def test_similarity_search(document_service, mock_document):
    # Arrange
    mock_documents = [mock_document]
    document_service.db.query.return_value.filter.return_value.all.return_value = mock_documents
    document_service.generate_embedding = Mock(return_value=[0.1, 0.2, 0.3])

    # Act
    documents = document_service.similarity_search(mock_document.user_id, "test query")

    # Assert
    assert len(documents) == 1
    assert documents[0].id == mock_document.id
    document_service.generate_embedding.assert_called_once_with("test query")
    document_service.db.query.assert_called_once_with(Document) 