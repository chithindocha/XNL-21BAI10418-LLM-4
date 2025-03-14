from pydantic import BaseModel

class ChatMessage(BaseModel):
    """Model for chat messages"""
    message: str
    user_id: str = "default" 