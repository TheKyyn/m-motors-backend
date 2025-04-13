"""
Tests pour le service RAG.
Ces tests utilisent des mocks pour éviter d'appeler réellement les API externes.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
import uuid
import json

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.services.rag_service import RAGService
from app.models.chat import Document, DocumentChunk, ChatSession, ChatMessage
from app.schemas.chat import ChatRequest
from app.database import Base


@pytest.fixture
async def async_db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def mock_rag_service():
    with patch("app.services.rag_service.OpenAIEmbeddings") as mock_embeddings, \
         patch("app.services.rag_service.ChatOpenAI") as mock_llm, \
         patch("app.services.rag_service.FAISS") as mock_faiss:
        
        mock_embeddings_instance = Mock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        mock_faiss.from_documents.return_value = Mock()
        mock_faiss.from_documents.return_value.similarity_search_with_score.return_value = [
            (Mock(page_content="Contenu pertinent", metadata={"source": "Document test"}), 0.1)
        ]
        
        service = RAGService()
        
        service.llm.invoke = AsyncMock(return_value="Réponse générée par le modèle")
        
        yield service


@pytest.mark.asyncio
async def test_add_document(async_db_session, mock_rag_service):
    """Teste l'ajout d'un document à la base de connaissances"""
    document = await mock_rag_service.add_document(
        db=async_db_session,
        title="Document de test",
        content="Ceci est le contenu du document de test.",
        metadata={"source": "test", "type": "markdown"}
    )
    
    assert document.id is not None
    assert document.title == "Document de test"
    assert document.content == "Ceci est le contenu du document de test."
    assert document.metadata == {"source": "test", "type": "markdown"}
    assert document.embedding_status is True
    
    chunks = document.chunks
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.document_id == document.id
        assert chunk.content != ""
        assert "source" in chunk.metadata


@pytest.mark.asyncio
async def test_create_or_get_session_new(async_db_session, mock_rag_service):
    """Teste la création d'une nouvelle session de chat"""
    chat_request = ChatRequest(
        message="Bonjour, je cherche des informations",
        user_id=1
    )
    
    session = await mock_rag_service.create_or_get_session(async_db_session, chat_request)
    
    assert session.id is not None
    assert session.user_id == 1
    assert session.session_id is not None
    
    result = await async_db_session.execute(
        f"SELECT * FROM rag_chat_messages WHERE session_id = {session.id}"
    )
    messages = result.fetchall()
    assert len(messages) == 1
    assert messages[0][2] == "system"


@pytest.mark.asyncio
async def test_create_or_get_session_existing(async_db_session, mock_rag_service):
    """Teste la récupération d'une session existante"""
    session = ChatSession(
        user_id=1,
        session_id=str(uuid.uuid4()),
        metadata={"test": True}
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    chat_request = ChatRequest(
        message="Suite de la conversation",
        session_id=session.session_id
    )
    
    retrieved_session = await mock_rag_service.create_or_get_session(async_db_session, chat_request)
    
    assert retrieved_session.id == session.id
    assert retrieved_session.session_id == session.session_id
    assert retrieved_session.user_id == 1


@pytest.mark.asyncio
async def test_store_message(async_db_session, mock_rag_service):
    """Teste le stockage d'un message"""
    session = ChatSession(
        user_id=1,
        session_id=str(uuid.uuid4())
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    message = await mock_rag_service.store_message(
        db=async_db_session,
        session_id=session.id,
        role="user",
        content="Message de test",
        metadata={"ip": "127.0.0.1"}
    )
    
    assert message.id is not None
    assert message.session_id == session.id
    assert message.role == "user"
    assert message.content == "Message de test"
    assert message.metadata == {"ip": "127.0.0.1"}
    assert message.created_at is not None


@pytest.mark.asyncio
async def test_get_relevant_documents(async_db_session, mock_rag_service):
    """Teste la récupération des documents pertinents"""
    document = Document(
        title="Document sur la location",
        content="Informations sur la location longue durée",
        metadata={"category": "location"},
        embedding_status=True
    )
    async_db_session.add(document)
    await async_db_session.commit()
    await async_db_session.refresh(document)
    
    chunk = DocumentChunk(
        document_id=document.id,
        content="La location longue durée est un service proposé par M-Motors",
        metadata={"source": document.title, "chunk_index": 0}
    )
    async_db_session.add(chunk)
    await async_db_session.commit()
    
    with patch("app.services.rag_service.FAISS") as mock_faiss:
        from langchain.schema import Document as LCDocument
        
        lc_doc = LCDocument(
            page_content="La location longue durée est un service proposé par M-Motors",
            metadata={"source": "Document sur la location", "doc_id": document.id, "chunk_id": chunk.id}
        )
        
        mock_vectorstore = Mock()
        mock_faiss.from_documents.return_value = mock_vectorstore
        mock_vectorstore.similarity_search_with_score.return_value = [(lc_doc, 0.2)]
        
        results = await mock_rag_service.get_relevant_documents(async_db_session, "location longue durée")
        
        assert len(results) == 1
        doc, score = results[0]
        assert doc.page_content == "La location longue durée est un service proposé par M-Motors"
        assert doc.metadata["source"] == "Document sur la location"
        assert score == 0.2


@pytest.mark.asyncio
async def test_generate_response(async_db_session, mock_rag_service):
    """Teste la génération d'une réponse complète"""
    chat_request = ChatRequest(
        message="Comment fonctionne la location longue durée ?",
        user_id=1
    )
    
    with patch.object(mock_rag_service, "create_or_get_session", autospec=True) as mock_get_session, \
         patch.object(mock_rag_service, "store_message", autospec=True) as mock_store_message, \
         patch.object(mock_rag_service, "get_relevant_documents", autospec=True) as mock_get_docs, \
         patch("langchain.chains.combine_documents.create_stuff_documents_chain") as mock_create_chain:
        
        session = ChatSession(id=1, user_id=1, session_id="test-session")
        mock_get_session.return_value = session
        
        user_message = ChatMessage(id=1, session_id=1, role="user", content=chat_request.message)
        mock_store_message.return_value = user_message
        
        from langchain.schema import Document as LCDocument
        lc_doc = LCDocument(
            page_content="La location longue durée permet d'utiliser un véhicule sur une période de 24 à 48 mois.",
            metadata={"source": "Services de location"}
        )
        mock_get_docs.return_value = [(lc_doc, 0.1)]
        
        mock_chain = Mock()
        mock_chain.invoke.return_value = "La location longue durée vous permet de profiter d'un véhicule pendant 24 à 48 mois avec diverses options incluses."
        mock_create_chain.return_value = mock_chain
        
        response = await mock_rag_service.generate_response(async_db_session, chat_request)
        
        assert response is not None
        assert "session_id" in response
        assert "response" in response
        assert "sources" in response
        assert response["session_id"] == "test-session"
        assert response["response"] == "La location longue durée vous permet de profiter d'un véhicule pendant 24 à 48 mois avec diverses options incluses."
        assert len(response["sources"]) == 1
        assert response["sources"][0]["title"] == "Services de location"
        
        mock_get_session.assert_called_once()
        assert mock_store_message.call_count == 2
        mock_get_docs.assert_called_once()
        mock_chain.invoke.assert_called_once() 