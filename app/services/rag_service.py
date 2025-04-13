import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.schema import Document as LangchainDocument

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from ..models.chat import Document, DocumentChunk, ChatSession, ChatMessage
from ..config import settings
from ..schemas.chat import ChatRequest, ChatSessionCreate, ChatMessageCreate

logger = logging.getLogger(__name__)


class RAGService:
    """Service pour gérer le RAG chat"""
    
    def __init__(self):
        # objets LangChain
        api_key = settings.OPENAI_API_KEY.get_secret_value() if settings.OPENAI_API_KEY else None
        
        try:
            self.embeddings = OpenAIEmbeddings(
                api_key=api_key,
                model="text-embedding-3-small"
            )
            
            self.llm = ChatOpenAI(
                api_key=api_key,
                model="gpt-3.5-turbo",
                temperature=0.2
            )
        except Exception as e:
            logger.error(f"Erreur d'initialisation des modèles OpenAI: {str(e)}")
            self.embeddings = None
            self.llm = None
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        # Template pour la génération des réponses
        self.prompt = ChatPromptTemplate.from_template("""
        Tu es un assistant virtuel pour M-Motors, spécialiste en vente et location de véhicules d'occasion.
        Tu fournis des informations précises sur les services, les procédures d'achat et de location de véhicules.
        Réponds poliment et de manière professionnelle aux questions des clients, en français uniquement.
        
        Contexte sur M-Motors:
        - Entreprise créée en 1987, spécialiste en vente de véhicules d'occasion
        - Propose une gamme variée de marques, modèles, motorisations
        - Offre des services comme: reprise d'ancien véhicule, financement, essai routier
        - Propose désormais un service de location longue durée avec option d'achat
        - Options incluses avec l'abonnement location: assurance tous risques, assistance dépannage, entretien et SAV, contrôle technique
        
        Utilisez les informations suivantes pour répondre à la question:
        {context}
        
        Question: {question}
        
        Réponse:
        """)
    
    async def initialize_vector_db(self, db: AsyncSession):
        """Initialise la base de données vectorielle à partir des documents stockés"""
        try:
            # récupération de tous les documents
            result = await db.execute(
                select(Document)
                .filter(Document.embedding_status == False)
                .options(selectinload(Document.chunks))
            )
            documents = result.scalars().all()
            
            for doc in documents:
                # diviser le doc
                chunks = self.text_splitter.split_text(doc.content)
                
                # embeddings et stockage
                for i, chunk_text in enumerate(chunks):
                    # chunk de document
                    db_chunk = DocumentChunk(
                        document_id=doc.id,
                        content=chunk_text,
                        meta_data={"source": doc.title, "chunk_index": i}
                    )
                    db.add(db_chunk)
                doc.embedding_status = True
            
            await db.commit()
            logger.info(f"Traitement de {len(documents)} documents terminé")
        except Exception as e:
            await db.rollback()
            logger.error(f"Erreur lors de l'initialisation de la base vectorielle: {str(e)}")
            raise
    
    async def add_document(self, db: AsyncSession, title: str, content: str, metadata: Optional[Dict] = None) -> Document:
        """Ajoute un nouveau document à la base de connaissances"""
        try:
            document = Document(title=title, content=content, meta_data=metadata, embedding_status=False)
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            chunks = self.text_splitter.split_text(content)
            
            for i, chunk_text in enumerate(chunks):
                db_chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_text,
                    meta_data={"source": title, "chunk_index": i}
                )
                db.add(db_chunk)
            
            document.embedding_status = True
            await db.commit()
            
            logger.info(f"Document '{title}' ajouté avec {len(chunks)} chunks")
            return document
        except Exception as e:
            await db.rollback()
            logger.error(f"Erreur lors de l'ajout du document: {str(e)}")
            raise
    
    async def create_or_get_session(self, db: AsyncSession, chat_request: ChatRequest) -> ChatSession:
        """Crée ou récupère une session de chat"""
        if chat_request.session_id:
            result = await db.execute(
                select(ChatSession)
                .filter(ChatSession.session_id == chat_request.session_id)
            )
            session = result.scalar_one_or_none()
            
            if session:
                session.last_activity = datetime.now()
                await db.commit()
                return session
        
        session_create = ChatSessionCreate(
            user_id=chat_request.user_id,
            metadata={"created_from": "api_request"}
        )
        
        session = ChatSession(
            user_id=session_create.user_id,
            session_id=session_create.session_id,
            meta_data=session_create.metadata
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        system_message = ChatMessage(
            session_id=session.id,
            role="system",
            content="Bienvenue chez M-Motors. Comment puis-je vous aider aujourd'hui ?"
        )
        db.add(system_message)
        await db.commit()
        
        return session
    
    async def store_message(self, db: AsyncSession, session_id: int, role: str, content: str, metadata: Optional[Dict] = None) -> ChatMessage:
        """Stocke un message dans la base de données"""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            meta_data=metadata
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message
    
    async def get_relevant_documents(self, db: AsyncSession, query: str, top_k: int = 3) -> List[Tuple[DocumentChunk, float]]:
        """Récupère les documents les plus pertinents pour la requête"""
        try:
            result = await db.execute(
                select(DocumentChunk)
                .options(selectinload(DocumentChunk.document))
            )
            chunks = result.scalars().all()
            
            if not chunks:
                logger.warning("Aucun chunk de document trouvé dans la base de données")
                return []
            
            if self.embeddings is None:
                logger.warning("Embeddings non initialisés, utilisation d'une recherche simple")
                return [(chunk, 0.5) for chunk in chunks[:top_k]]
            
            docs = [
                LangchainDocument(
                    page_content=chunk.content,
                    metadata={
                        "source": chunk.document.title if chunk.document else "Unknown",
                        "doc_id": chunk.document_id,
                        "chunk_id": chunk.id
                    }
                )
                for chunk in chunks
            ]
            
            vectorstore = FAISS.from_documents(docs, self.embeddings)
            
            relevant_docs = vectorstore.similarity_search_with_score(query, k=top_k)
            
            return relevant_docs
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents pertinents: {str(e)}")
            return []
    
    async def generate_response(self, db: AsyncSession, chat_request: ChatRequest) -> Dict[str, Any]:
        """Génère une réponse à la requête de l'utilisateur"""
        try:
            session = await self.create_or_get_session(db, chat_request)
            
            await self.store_message(db, session.id, "user", chat_request.message)
            
            relevant_docs_with_scores = await self.get_relevant_documents(db, chat_request.message)
            
            if relevant_docs_with_scores:
                relevant_docs = [doc for doc, _ in relevant_docs_with_scores]
                sources = [
                    {
                        "title": doc.metadata.get("source", "Unknown"),
                        "relevance": round((1 - score) * 100, 2)  # Convertir en pourcentage de pertinence
                    }
                    for doc, score in relevant_docs_with_scores
                ]
            else:
                relevant_docs = [
                    LangchainDocument(
                        page_content="Aucune information spécifique trouvée. Utilisez les informations générales sur M-Motors.",
                        metadata={"source": "Informations générales"}
                    )
                ]
                sources = []
            
            if self.llm is None:
                response = "Je suis désolé, le service de génération de réponses n'est pas disponible actuellement. Veuillez réessayer plus tard ou contacter le support."
            else:
                document_chain = create_stuff_documents_chain(self.llm, self.prompt)
                response = document_chain.invoke({
                    "context": relevant_docs,
                    "question": chat_request.message
                })
            
            await self.store_message(
                db, 
                session.id, 
                "assistant", 
                response,
                metadata={"sources": sources}
            )
            
            return {
                "session_id": session.session_id,
                "response": response,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la réponse: {str(e)}")
            raise 