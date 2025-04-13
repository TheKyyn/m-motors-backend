from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import logging

from ..database import get_db
from ..schemas.chat import (
    DocumentCreate, 
    DocumentResponse, 
    ChatRequest, 
    ChatResponse,
    ChatSessionResponse
)
from ..models.chat import Document, ChatSession
from ..services.rag_service import RAGService
from ..security import get_current_user
from sqlalchemy import select

logger = logging.getLogger(__name__)

# router
rag_router = APIRouter(prefix="/api/v1/rag", tags=["rag-chat"])

# service RAG
rag_service = RAGService()


@rag_router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def add_document(
    document: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Ajoute un document à la base de connaissances du RAG"""
    try:
        result = await rag_service.add_document(
            db=db,
            title=document.title,
            content=document.content,
            metadata=document.metadata
        )
        return result
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'ajout du document"
        )


@rag_router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Récupère la liste des documents dans la base de connaissances"""
    try:
        result = await db.execute(select(Document))
        documents = result.scalars().all()
        return documents
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des documents"
        )


@rag_router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Récupère un document spécifique par son ID"""
    try:
        result = await db.execute(select(Document).filter(Document.id == document_id))
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document non trouvé"
            )
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du document"
        )


@rag_router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Endpoint pour discuter avec le RAG assistant"""
    try:
        if not chat_request.user_id and current_user:
            chat_request.user_id = current_user.id
            
        response = await rag_service.generate_response(db, chat_request)
        return response
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la réponse: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la génération de la réponse"
        )


@rag_router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Récupère les sessions de chat de l'utilisateur"""
    try:
        result = await db.execute(
            select(ChatSession)
            .filter(ChatSession.user_id == current_user.id)
        )
        sessions = result.scalars().all()
        return sessions
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des sessions"
        )


@rag_router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Récupère une session de chat spécifique"""
    try:
        result = await db.execute(
            select(ChatSession)
            .filter(ChatSession.session_id == session_id)
            .filter(ChatSession.user_id == current_user.id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée"
            )
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de la session"
        )


@rag_router.post("/guest/chat", response_model=ChatResponse)
async def guest_chat(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint pour les utilisateurs non authentifiés (invités)"""
    try:
        response = await rag_service.generate_response(db, chat_request)
        return response
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la réponse: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la génération de la réponse"
        ) 