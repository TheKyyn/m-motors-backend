"""
Tests pour les modèles du système RAG.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import json

from app.models.chat import Document, DocumentChunk, ChatSession, ChatMessage
from app.database import Base

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


def test_document_model(db_session: Session):
    """Teste le modèle Document"""
    document = Document(
        title="Test Document",
        content="Ceci est un document de test",
        metadata={"source": "test", "type": "markdown"},
        embedding_status=False
    )
    
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    
    assert document.id is not None
    assert document.title == "Test Document"
    assert document.content == "Ceci est un document de test"
    assert document.metadata == {"source": "test", "type": "markdown"}
    assert document.embedding_status is False
    assert document.created_at is not None
    
    assert document.chunks == []


def test_document_chunk_model(db_session: Session):
    """Teste le modèle DocumentChunk"""
    document = Document(
        title="Test Document",
        content="Ceci est un document de test",
        metadata={"source": "test"},
        embedding_status=False
    )
    db_session.add(document)
    db_session.commit()
    
    chunk = DocumentChunk(
        document_id=document.id,
        content="Ceci est un chunk de test",
        metadata={"index": 0},
        embedding="[0.1, 0.2, 0.3]"
    )
    db_session.add(chunk)
    db_session.commit()
    db_session.refresh(chunk)
    db_session.refresh(document)
    
    assert chunk.id is not None
    assert chunk.document_id == document.id
    assert chunk.content == "Ceci est un chunk de test"
    assert chunk.metadata == {"index": 0}
    assert chunk.embedding == "[0.1, 0.2, 0.3]"
    
    assert chunk.document == document
    assert document.chunks == [chunk]


def test_chat_session_model(db_session: Session):
    """Teste le modèle ChatSession"""
    session = ChatSession(
        user_id=1,
        session_id="test-session-id",
        metadata={"client_info": "test client"}
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    assert session.id is not None
    assert session.user_id == 1
    assert session.session_id == "test-session-id"
    assert session.metadata == {"client_info": "test client"}
    assert session.created_at is not None
    assert session.last_activity is not None
    
    assert session.messages == []


def test_chat_message_model(db_session: Session):
    """Teste le modèle ChatMessage"""
    session = ChatSession(
        user_id=1,
        session_id="test-session-id"
    )
    db_session.add(session)
    db_session.commit()
    
    message = ChatMessage(
        session_id=session.id,
        role="user",
        content="Bonjour, j'ai une question sur la location.",
        metadata={"client_ip": "127.0.0.1"}
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    db_session.refresh(session)
    
    assert message.id is not None
    assert message.session_id == session.id
    assert message.role == "user"
    assert message.content == "Bonjour, j'ai une question sur la location."
    assert message.metadata == {"client_ip": "127.0.0.1"}
    assert message.created_at is not None
    
    assert message.session == session
    assert session.messages == [message]


def test_document_cascade_delete(db_session: Session):
    """Teste la suppression en cascade des chunks lorsqu'un document est supprimé"""
    document = Document(
        title="Document à supprimer",
        content="Contenu du document",
        embedding_status=False
    )
    db_session.add(document)
    db_session.commit()
    
    for i in range(3):
        chunk = DocumentChunk(
            document_id=document.id,
            content=f"Chunk {i}",
            metadata={"index": i}
        )
        db_session.add(chunk)
    db_session.commit()
    
    chunks = db_session.query(DocumentChunk).filter_by(document_id=document.id).all()
    assert len(chunks) == 3
    
    db_session.delete(document)
    db_session.commit()
    
    chunks = db_session.query(DocumentChunk).filter_by(document_id=document.id).all()
    assert len(chunks) == 0


def test_chat_session_cascade_delete(db_session: Session):
    """Teste la suppression en cascade des messages lorsqu'une session est supprimée"""
    session = ChatSession(
        user_id=1,
        session_id="session-to-delete"
    )
    db_session.add(session)
    db_session.commit()
    
    for i in range(3):
        message = ChatMessage(
            session_id=session.id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}"
        )
        db_session.add(message)
    db_session.commit()
    
    messages = db_session.query(ChatMessage).filter_by(session_id=session.id).all()
    assert len(messages) == 3
    
    db_session.delete(session)
    db_session.commit()
    
    messages = db_session.query(ChatMessage).filter_by(session_id=session.id).all()
    assert len(messages) == 0 