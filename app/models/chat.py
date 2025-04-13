from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from ..database import Base


class Document(Base):
    """Modèle pour stocker les documents de base de connaissances"""
    __tablename__ = "rag_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    meta_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    embedding_status = Column(Boolean, default=False)
    
    # Relations
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Modèle pour stocker les chunks de documents pour la recherche sémantique"""
    __tablename__ = "rag_document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("rag_documents.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    meta_data = Column(JSONB, nullable=True)
    embedding = Column(Text, nullable=True)
    
    # Relations
    document = relationship("Document", back_populates="chunks")


class ChatSession(Base):
    """Modèle pour stocker les sessions de chat des utilisateurs"""
    __tablename__ = "rag_chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meta_data = Column(JSONB, nullable=True)
    
    # Relations
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Modèle pour stocker les messages de chat"""
    __tablename__ = "rag_chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("rag_chat_sessions.id", ondelete="CASCADE"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSONB, nullable=True)
    
    # Relations
    session = relationship("ChatSession", back_populates="messages") 