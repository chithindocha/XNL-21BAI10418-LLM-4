import pytest
from app.services.chat_service import ChatService
from app.services.vector_store import VectorStore
from unittest.mock import Mock, patch

@pytest.fixture
def chat_service():
    return ChatService()

@pytest.fixture
def vector_store():
    return VectorStore()

@pytest.mark.asyncio
async def test_generate_response(chat_service):
    """Test basic response generation"""
    message = "What is a good investment strategy?"
    response = await chat_service.generate_response(message)
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)

@pytest.mark.asyncio
async def test_generate_response_with_context(chat_service, vector_store):
    """Test response generation with context"""
    # Add some test context
    await vector_store.add_document(
        content="Diversification is key to a good investment strategy.",
        source="test_doc"
    )
    
    message = "What is a good investment strategy?"
    context = await vector_store.get_relevant_context(message)
    
    response = await chat_service.generate_response(
        message,
        context=context
    )
    
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)

@pytest.mark.asyncio
async def test_fallback_response(chat_service):
    """Test fallback response when LLM fails"""
    with patch.object(chat_service.client, 'chat_completion', side_effect=Exception("Test error")):
        response = await chat_service.generate_response("Test message")
        assert response is not None
        assert len(response) > 0
        assert "apologize" in response.lower()
        assert "trouble" in response.lower()

@pytest.mark.asyncio
async def test_vector_store_operations(vector_store):
    """Test vector store operations"""
    # Test adding document
    await vector_store.add_document(
        content="Test document content",
        source="test_source"
    )
    
    # Test retrieving context
    context = await vector_store.get_relevant_context("test query")
    assert context is not None
    assert len(context) > 0
    
    # Test document deletion
    await vector_store.delete_document(0)
    context = await vector_store.get_relevant_context("test query")
    assert len(context) == 0

@pytest.mark.asyncio
async def test_chat_history(chat_service):
    """Test chat history functionality"""
    # Test getting empty history
    history = await chat_service.get_chat_history("test_user")
    assert isinstance(history, list)
    assert len(history) == 0
    
    # Test storing conversation
    await chat_service._store_conversation(
        "test_user",
        "Test message",
        "Test response"
    )
    
    # Note: In a real implementation, we would test retrieving the stored conversation
    # This would require setting up a test database 