# Système de RAG Chat pour M-Motors

Ce document explique comment utiliser et configurer le système de RAG (Retrieval Augmented Generation) Chat implémenté pour M-Motors.

## Qu'est-ce que le RAG ?

Le RAG (Retrieval Augmented Generation) est une approche qui combine la recherche d'informations pertinentes à partir d'une base de connaissances avec la génération de texte à l'aide d'un modèle de langage. Dans notre cas, le système utilise les documents stockés concernant M-Motors pour fournir des réponses précises et contextuelles aux questions des clients.

## Configuration requise

1. Une clé API OpenAI valide (à configurer dans le fichier `.env`)
2. Une base de données PostgreSQL (la même que celle utilisée par l'application principale)

## Installation

Le système RAG est intégré à l'API M-Motors. Pour l'installer :

1. Mettez à jour le fichier `.env` avec votre clé API OpenAI :
   ```
   OPENAI_API_KEY="votre_clé_api_openai"
   ```

2. Exécutez les migrations pour créer les tables nécessaires :
   ```bash
   alembic upgrade head
   ```

3. Chargez des documents initiaux dans la base de connaissances :
   ```bash
   python -m scripts.load_rag_documents --sample
   ```

## Utilisation des API

### Endpoints pour l'administration (authentification requise)

- **Ajouter un document** : `POST /api/v1/rag/documents`
  ```json
  {
    "title": "Titre du document",
    "content": "Contenu du document à indexer...",
    "metadata": {"source": "manuel", "categorie": "vehicules"}
  }
  ```

- **Récupérer tous les documents** : `GET /api/v1/rag/documents`

- **Récupérer un document spécifique** : `GET /api/v1/rag/documents/{document_id}`

- **Discuter avec l'assistant (utilisateurs authentifiés)** : `POST /api/v1/rag/chat`
  ```json
  {
    "message": "Quelles sont les options incluses dans le service de location longue durée ?",
    "session_id": "UUID_optionnel_pour_continuer_une_conversation"
  }
  ```

- **Récupérer les sessions de chat** : `GET /api/v1/rag/sessions`

- **Récupérer une session de chat spécifique** : `GET /api/v1/rag/sessions/{session_id}`

### Endpoint public (sans authentification)

- **Discuter avec l'assistant (invités)** : `POST /api/v1/rag/guest/chat`
  ```json
  {
    "message": "Comment fonctionne la location longue durée ?",
    "session_id": "UUID_optionnel_pour_continuer_une_conversation"
  }
  ```

## Ajout de documents à la base de connaissances

Vous pouvez ajouter des documents de plusieurs façons :

1. **Via l'API** : En utilisant l'endpoint `POST /api/v1/rag/documents`

2. **Via le script utilitaire** :
   
   - Pour charger les documents d'exemple :
     ```bash
     python -m scripts.load_rag_documents --sample
     ```
   
   - Pour charger des documents à partir d'un répertoire :
     ```bash
     python -m scripts.load_rag_documents --input ./documents/ --format markdown
     ```

## Format de la réponse du chat

Lorsque vous utilisez les endpoints de chat, la réponse a la structure suivante :

```json
{
  "session_id": "uuid_de_la_session",
  "response": "Réponse générée par l'IA...",
  "sources": [
    {
      "title": "Titre du document source",
      "relevance": 95.42
    },
    {
      "title": "Autre document source",
      "relevance": 87.12
    }
  ]
}
```

Le champ `sources` indique les documents qui ont été utilisés pour générer la réponse, avec leur pourcentage de pertinence.

## Personnalisation

Le comportement du chatbot peut être personnalisé en modifiant le template de prompt dans le fichier `app/services/rag_service.py`.

## Dépannage

1. **Erreur d'API OpenAI** : Vérifiez que votre clé API est valide et que vous avez des crédits suffisants.

2. **Problèmes de base de données** : Assurez-vous que les migrations ont été correctement appliquées.

3. **Réponses non pertinentes** : Vérifiez si vous avez chargé suffisamment de documents pertinents dans la base de connaissances.

## Limitations actuelles

- Le système utilise actuellement OpenAI comme fournisseur de modèle. Pour utiliser d'autres fournisseurs, des modifications du code seraient nécessaires.
- La recherche vectorielle est effectuée en mémoire à chaque requête. Pour une utilisation à grande échelle, il serait préférable d'utiliser une base de données vectorielle persistante. 