"""
Tests pour les API endpoints du système RAG.
"""
import pytest
import unittest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import asyncio
from datetime import datetime
import json

from app.database import get_db
from app.routers.rag_router import rag_router, rag_service
from app.security import get_current_user


class TestRAGEndpoints(unittest.TestCase):
    """Tests unitaires pour les endpoints du RAG API"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.app = FastAPI()
        
        async def mock_get_db():
            return AsyncMock()
            
        async def mock_get_current_user():
            return {"id": 1, "username": "testuser"}
            
        self.app.dependency_overrides = {
            get_db: mock_get_db,
            get_current_user: mock_get_current_user
        }
        
        self.app.include_router(rag_router)
        self.client = TestClient(self.app)
        
        self.mock_rag_service = AsyncMock()
        self.original_rag_service = rag_service
        with patch("app.routers.rag_router.rag_service", self.mock_rag_service):
            pass

    def tearDown(self):
        """Nettoyage après chaque test"""
        rag_router.dependencies[0].dependency = self.original_rag_service
        self.app.dependency_overrides = {}

    def test_add_document(self):
        """Test d'ajout d'un document"""
        mock_doc = {
            "id": 1,
            "title": "Document de test",
            "content": "Contenu du document",
            "meta_data": {"source": "test"},
            "created_at": datetime.now().isoformat(),
            "updated_at": None,
            "embedding_status": True
        }
        
        future = asyncio.Future()
        future.set_result(mock_doc)
        self.mock_rag_service.add_document.return_value = future
        
        with patch("app.routers.rag_router.rag_service", self.mock_rag_service):
            response = self.client.post(
                "/api/v1/rag/documents",
                json={
                    "title": "Document de test",
                    "content": "Contenu du document",
                    "metadata": {"source": "test"}
                }
            )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "Document de test")
        self.assertEqual(data["content"], "Contenu du document")
        self.assertIn("id", data)
        self.assertEqual(data["id"], 1)

    def test_get_documents(self):
        """Test de récupération des documents"""
        mock_db = AsyncMock()
        mock_result = Mock()
        
        mock_docs = [
            {
                "id": 1,
                "title": "Document 1",
                "content": "Contenu 1",
                "meta_data": {},
                "created_at": datetime.now().isoformat(),
                "updated_at": None,
                "embedding_status": True
            },
            {
                "id": 2,
                "title": "Document 2",
                "content": "Contenu 2",
                "meta_data": {},
                "created_at": datetime.now().isoformat(),
                "updated_at": None,
                "embedding_status": True
            }
        ]
        
        with patch("app.routers.rag_router.get_db", return_value=mock_db), \
             patch("app.routers.rag_router.rag_service", self.mock_rag_service):
            mock_result.scalars().all.return_value = mock_docs
            future = asyncio.Future()
            future.set_result(mock_result)
            mock_db.execute.return_value = future
            
            response = self.client.get("/api/v1/rag/documents")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["title"], "Document 1")
            self.assertEqual(data[1]["title"], "Document 2")

    def test_chat_endpoint(self):
        """Test de l'endpoint de chat"""
        mock_response = {
            "session_id": "test-session-id",
            "response": "Voici la réponse à votre question",
            "sources": [{"title": "Source 1", "relevance": 95.5}]
        }
        
        future = asyncio.Future()
        future.set_result(mock_response)
        self.mock_rag_service.generate_response.return_value = future
        
        with patch("app.routers.rag_router.rag_service", self.mock_rag_service):
            response = self.client.post(
                "/api/v1/rag/chat",
                json={
                    "message": "Question de test",
                    "session_id": None
                }
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["session_id"], "test-session-id")
        self.assertEqual(data["response"], "Voici la réponse à votre question")
        self.assertEqual(len(data["sources"]), 1)

    def test_guest_chat_endpoint(self):
        """Test de l'endpoint de chat pour invités"""
        async def mock_get_current_user_unauthorized():
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Non authentifié")
            
        original_override = self.app.dependency_overrides[get_current_user]
        self.app.dependency_overrides[get_current_user] = mock_get_current_user_unauthorized
        
        try:
            mock_response = {
                "session_id": "guest-session-id",
                "response": "Réponse à l'invité",
                "sources": []
            }
            
            future = asyncio.Future()
            future.set_result(mock_response)
            self.mock_rag_service.generate_response.return_value = future
            
            with patch("app.routers.rag_router.rag_service", self.mock_rag_service):
                response = self.client.post(
                    "/api/v1/rag/guest/chat",
                    json={
                        "message": "Question d'un invité",
                        "session_id": None
                    }
                )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["session_id"], "guest-session-id")
            self.assertEqual(data["response"], "Réponse à l'invité")
            
        finally:
            self.app.dependency_overrides[get_current_user] = original_override

    def test_error_handling(self):
        """Test de la gestion des erreurs"""
        self.mock_rag_service.add_document.side_effect = Exception("Erreur de test")
        
        with patch("app.routers.rag_router.rag_service", self.mock_rag_service):
            response = self.client.post(
                "/api/v1/rag/documents",
                json={
                    "title": "Document qui échoue",
                    "content": "Contenu",
                    "metadata": {"source": "test"}
                }
            )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("Erreur", data["detail"]) 