from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class DocumentBase(BaseModel):
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    embedding_status: bool

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    role: str = Field(..., description="Le rôle du message: 'user', 'assistant' ou 'system'")
    content: str = Field(..., description="Le contenu du message")


class ChatMessageCreate(ChatMessageBase):
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(ChatMessageBase):
    id: int
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    user_id: Optional[int] = None
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Optional[Dict[str, Any]] = None


class ChatSessionResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    session_id: str
    created_at: datetime
    last_activity: datetime
    metadata: Optional[Dict[str, Any]] = None
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    user_id: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: Optional[List[Dict[str, Any]]] = None 