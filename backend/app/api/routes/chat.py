from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.auth import get_current_user
from app.services.chat_service import ChatService
from app.services.vector_store import VectorStore

router = APIRouter()

class ChatMessage(BaseModel):
    content: str
    timestamp: Optional[datetime] = None
    context_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    timestamp: datetime
    context_used: Optional[List[str]] = None

@router.post("/message", response_model=ChatResponse)
async def send_message(
    message: ChatMessage,
    current_user = Depends(get_current_user),
    chat_service: ChatService = Depends(),
    vector_store: VectorStore = Depends()
):
    """
    Process a chat message and return a response with relevant context
    """
    try:
        # Get relevant context from vector store
        context = await vector_store.get_relevant_context(message.content)
        
        # Generate response using LLM with context
        response = await chat_service.generate_response(
            message.content,
            context=context,
            user_id=current_user.id
        )
        
        return ChatResponse(
            message=response,
            timestamp=datetime.utcnow(),
            context_used=[c["source"] for c in context] if context else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/history", response_model=List[ChatResponse])
async def get_chat_history(
    current_user = Depends(get_current_user),
    chat_service: ChatService = Depends(),
    limit: int = 50,
    before: Optional[datetime] = None
):
    """
    Retrieve chat history for the current user
    """
    try:
        history = await chat_service.get_chat_history(
            user_id=current_user.id,
            limit=limit,
            before=before
        )
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@router.post("/context/upload")
async def upload_context(
    content: str,
    source: str,
    current_user = Depends(get_current_user),
    vector_store: VectorStore = Depends()
):
    """
    Upload new context to the vector store
    """
    try:
        await vector_store.add_document(content, source)
        return {"message": "Context uploaded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading context: {str(e)}"
        ) 