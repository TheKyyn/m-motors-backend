"""
Tests pour les schémas Pydantic du système RAG.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
import uuid

from app.schemas.chat import (
    DocumentBase, DocumentCreate, DocumentResponse,
    ChatMessageBase, ChatMessageCreate, ChatMessageResponse,
    ChatSessionCreate, ChatSessionResponse,
    ChatRequest, ChatResponse
)


def test_document_base_schema():
    """Teste le schéma DocumentBase"""
    doc = DocumentBase(
        title="Test Document",
        content="Contenu du document",
        metadata={"source": "test"}
    )
    assert doc.title == "Test Document"
    assert doc.content == "Contenu du document"
    assert doc.metadata == {"source": "test"}
    
    doc = DocumentBase(
        title="Titre seulement",
        content="Contenu"
    )
    assert doc.title == "Titre seulement"
    assert doc.content == "Contenu"
    assert doc.metadata is None
    
    with pytest.raises(ValidationError):
        doc = DocumentBase(title="Titre uniquement")
    
    with pytest.raises(ValidationError):
        doc = DocumentBase(content="Contenu uniquement")


def test_document_create_schema():
    """Teste le schéma DocumentCreate"""
    doc = DocumentCreate(
        title="Document à créer",
        content="Contenu du document à créer"
    )
    assert doc.title == "Document à créer"
    assert doc.content == "Contenu du document à créer"
    assert doc.metadata is None


def test_document_response_schema():
    """Teste le schéma DocumentResponse"""
    doc = DocumentResponse(
        id=1,
        title="Document de réponse",
        content="Contenu du document de réponse",
        metadata={"source": "test"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        embedding_status=True
    )
    assert doc.id == 1
    assert doc.title == "Document de réponse"
    assert doc.content == "Contenu du document de réponse"
    assert doc.metadata == {"source": "test"}
    assert isinstance(doc.created_at, datetime)
    assert isinstance(doc.updated_at, datetime)
    assert doc.embedding_status is True
    
    doc = DocumentResponse(
        id=2,
        title="Document sans mise à jour",
        content="Contenu",
        created_at=datetime.now(),
        embedding_status=False
    )
    assert doc.id == 2
    assert doc.title == "Document sans mise à jour"
    assert doc.updated_at is None
    assert doc.metadata is None
    assert doc.embedding_status is False


def test_chat_message_base_schema():
    """Teste le schéma ChatMessageBase"""
    msg = ChatMessageBase(
        role="user",
        content="Bonjour, j'ai une question"
    )
    assert msg.role == "user"
    assert msg.content == "Bonjour, j'ai une question"
    
    msg = ChatMessageBase(role="assistant", content="Je peux vous aider")
    assert msg.role == "assistant"
    
    msg = ChatMessageBase(role="system", content="Message système")
    assert msg.role == "system"
    
    with pytest.raises(ValidationError):
        msg = ChatMessageBase(role="user")
    
    with pytest.raises(ValidationError):
        msg = ChatMessageBase(content="Message sans rôle")


def test_chat_message_create_schema():
    """Teste le schéma ChatMessageCreate"""
    msg = ChatMessageCreate(
        role="user",
        content="Contenu du message",
        metadata={"ip": "127.0.0.1"}
    )
    assert msg.role == "user"
    assert msg.content == "Contenu du message"
    assert msg.metadata == {"ip": "127.0.0.1"}
    
    msg = ChatMessageCreate(
        role="assistant",
        content="Réponse de l'assistant"
    )
    assert msg.role == "assistant"
    assert msg.content == "Réponse de l'assistant"
    assert msg.metadata is None


def test_chat_message_response_schema():
    """Teste le schéma ChatMessageResponse"""
    msg = ChatMessageResponse(
        id=1,
        role="user",
        content="Message de l'utilisateur",
        created_at=datetime.now(),
        metadata={"source": "api"}
    )
    assert msg.id == 1
    assert msg.role == "user"
    assert msg.content == "Message de l'utilisateur"
    assert isinstance(msg.created_at, datetime)
    assert msg.metadata == {"source": "api"}
    
    msg = ChatMessageResponse(
        id=2,
        role="assistant",
        content="Réponse de l'assistant",
        created_at=datetime.now()
    )
    assert msg.id == 2
    assert msg.metadata is None


def test_chat_session_create_schema():
    """Teste le schéma ChatSessionCreate"""
    session = ChatSessionCreate(
        user_id=1,
        metadata={"browser": "Chrome"}
    )
    assert session.user_id == 1
    assert session.metadata == {"browser": "Chrome"}
    assert session.session_id is not None
    
    custom_session_id = str(uuid.uuid4())
    session = ChatSessionCreate(
        session_id=custom_session_id
    )
    assert session.user_id is None
    assert session.session_id == custom_session_id
    assert session.metadata is None


def test_chat_session_response_schema():
    """Teste le schéma ChatSessionResponse"""
    messages = [
        ChatMessageResponse(
            id=1,
            role="user",
            content="Message 1",
            created_at=datetime.now()
        ),
        ChatMessageResponse(
            id=2,
            role="assistant",
            content="Réponse 1",
            created_at=datetime.now()
        )
    ]
    
    session = ChatSessionResponse(
        id=1,
        user_id=5,
        session_id="test-session",
        created_at=datetime.now(),
        last_activity=datetime.now(),
        metadata={"source": "api"},
        messages=messages
    )
    assert session.id == 1
    assert session.user_id == 5
    assert session.session_id == "test-session"
    assert isinstance(session.created_at, datetime)
    assert isinstance(session.last_activity, datetime)
    assert session.metadata == {"source": "api"}
    assert len(session.messages) == 2
    assert session.messages[0].content == "Message 1"
    assert session.messages[1].content == "Réponse 1"
    
    session = ChatSessionResponse(
        id=2,
        user_id=None,
        session_id="empty-session",
        created_at=datetime.now(),
        last_activity=datetime.now()
    )
    assert session.id == 2
    assert session.user_id is None
    assert session.messages == []
    assert session.metadata is None


def test_chat_request_schema():
    """Teste le schéma ChatRequest"""
    req = ChatRequest(
        session_id="existing-session",
        message="Bonjour, j'ai une question sur la location",
        user_id=10
    )
    assert req.session_id == "existing-session"
    assert req.message == "Bonjour, j'ai une question sur la location"
    assert req.user_id == 10
    
    req = ChatRequest(
        message="Question sans session"
    )
    assert req.message == "Question sans session"
    assert req.session_id is None
    assert req.user_id is None
    
    with pytest.raises(ValidationError):
        req = ChatRequest(session_id="session-sans-message")


def test_chat_response_schema():
    """Teste le schéma ChatResponse"""
    sources = [
        {"title": "Document 1", "relevance": 95.5},
        {"title": "Document 2", "relevance": 80.2}
    ]
    
    resp = ChatResponse(
        session_id="test-session",
        response="Voici la réponse à votre question...",
        sources=sources
    )
    assert resp.session_id == "test-session"
    assert resp.response == "Voici la réponse à votre question..."
    assert len(resp.sources) == 2
    assert resp.sources[0]["title"] == "Document 1"
    assert resp.sources[0]["relevance"] == 95.5
    
    resp = ChatResponse(
        session_id="another-session",
        response="Réponse sans sources"
    )
    assert resp.session_id == "another-session"
    assert resp.response == "Réponse sans sources"
    assert resp.sources is None 