#!/usr/bin/env python
"""
Script pour charger des documents dans la base de connaissances RAG.
Utilisation:
    python -m scripts.load_rag_documents --input ./documents/ --format markdown
"""

import os
import argparse
import asyncio
import logging
from typing import List, Dict, Any, Optional

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.services.rag_service import RAGService
from app.models.chat import Document

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


SAMPLE_DOCUMENTS = [
    {
        "title": "Services de location longue durée",
        "content": """
# Location Longue Durée chez M-Motors

M-Motors propose désormais un service de location longue durée avec option d'achat. 
Ce service vous permet de profiter d'un véhicule sans vous soucier des contraintes 
liées à la propriété.

## Services inclus dans l'abonnement location

- Assurance tous risques
- Assistance dépannage 24h/24 et 7j/7
- Entretien complet du véhicule
- Service après-vente prioritaire
- Contrôle technique

## Procédure de souscription

1. Sélectionnez le véhicule qui vous intéresse sur notre site
2. Choisissez la durée de location (24, 36 ou 48 mois)
3. Créez votre compte client ou connectez-vous
4. Téléchargez les documents requis pour votre dossier
5. Suivez l'avancement de votre dossier depuis votre espace client
6. Après validation, prenez rendez-vous pour récupérer votre véhicule

Pour plus d'informations, n'hésitez pas à contacter notre service client.
        """
    },
    {
        "title": "Procédure d'achat de véhicule",
        "content": """
# Acheter un véhicule chez M-Motors

M-Motors, spécialiste de la vente de véhicules d'occasion depuis 1987, 
vous propose une procédure d'achat simple et transparente.

## Étapes d'achat

1. Recherchez votre véhicule idéal parmi notre sélection
2. Prenez rendez-vous pour un essai routier
3. Si le véhicule vous convient, créez votre compte ou connectez-vous
4. Téléchargez les documents nécessaires à votre dossier d'achat
5. Choisissez votre mode de financement (comptant, crédit, LOA)
6. Suivez l'avancement de votre dossier dans votre espace client
7. Après validation, fixez la date de livraison de votre véhicule

## Services complémentaires

- Reprise de votre ancien véhicule
- Solutions de financement personnalisées
- Garantie véhicule de 12 à 24 mois
- Extension de garantie disponible

Pour toute question concernant l'achat d'un véhicule, notre équipe commerciale 
est à votre disposition.
        """
    },
    {
        "title": "FAQ - Questions fréquentes",
        "content": """
# Questions fréquentes - M-Motors

## Général

**Q: Quels sont les horaires d'ouverture de M-Motors ?**
R: Nos concessions sont ouvertes du lundi au samedi de 9h à 19h sans interruption.

**Q: Où sont situées vos concessions ?**
R: M-Motors dispose de 12 concessions réparties sur tout le territoire national. 
Consultez notre site pour trouver la concession la plus proche de chez vous.

## Location longue durée

**Q: Puis-je résilier mon contrat de location avant son terme ?**
R: Oui, mais des frais de résiliation anticipée s'appliquent. Ces frais sont dégressifs en fonction 
de la durée déjà écoulée du contrat.

**Q: Que se passe-t-il en cas de panne du véhicule loué ?**
R: Notre service d'assistance dépannage est inclus dans votre abonnement. Il est disponible 24h/24 et 7j/7. 
Un véhicule de remplacement sera mis à votre disposition si nécessaire.

**Q: Puis-je acheter le véhicule à la fin de ma période de location ?**
R: Oui, vous avez la possibilité d'acheter le véhicule à la fin du contrat de location à un prix défini 
à l'avance dans votre contrat.

## Achat de véhicule

**Q: Proposez-vous des garanties sur les véhicules d'occasion ?**
R: Oui, tous nos véhicules d'occasion bénéficient d'une garantie minimum de 12 mois, extensible à 24 mois.

**Q: Comment fonctionne le service de reprise de mon ancien véhicule ?**
R: Nous évaluons gratuitement votre véhicule et vous proposons un prix de reprise. 
Si vous acceptez, le montant est déduit du prix d'achat de votre nouveau véhicule.

**Q: Quels documents dois-je fournir pour acheter un véhicule ?**
R: Vous devez fournir une pièce d'identité valide, un justificatif de domicile de moins de 3 mois, 
et votre permis de conduire. Pour un financement, des justificatifs de revenus sont également nécessaires.
        """
    },
]


async def setup_db():
    """Configure la connexion à la base de données"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session


async def load_sample_documents():
    """Charge les documents d'exemple dans la base de connaissances"""
    try:
        async_session = await setup_db()
        rag_service = RAGService()
        
        async with async_session() as session:
            # Vérifier si des documents existent déjà
            result = await session.execute(sqlalchemy.select(sqlalchemy.func.count()).select_from(Document))
            count = result.scalar()
            
            if count > 0:
                logger.info(f"{count} documents déjà présents dans la base de données.")
                user_input = input("Voulez-vous continuer et ajouter de nouveaux documents ? (o/n): ").lower()
                if user_input != 'o':
                    return
            
            # Charger les documents d'exemple
            for doc in SAMPLE_DOCUMENTS:
                logger.info(f"Ajout du document: {doc['title']}")
                await rag_service.add_document(
                    db=session, 
                    title=doc['title'],
                    content=doc['content'],
                    metadata={"source": "exemple", "type": "markdown"}
                )
            
            logger.info(f"✅ {len(SAMPLE_DOCUMENTS)} documents d'exemple chargés avec succès !")
    except Exception as e:
        logger.error(f"Erreur lors du chargement des documents: {str(e)}")


async def load_documents_from_files(directory: str, file_format: str = "markdown"):
    """Charge des documents à partir de fichiers"""
    try:
        if not os.path.exists(directory):
            logger.error(f"Le répertoire {directory} n'existe pas.")
            return
        
        # Initialiser la session DB et le service RAG
        async_session = await setup_db()
        rag_service = RAGService()
        
        # Extensions supportées
        extensions = {
            "markdown": [".md", ".markdown"],
            "text": [".txt"],
            "html": [".html", ".htm"],
        }
        
        supported_extensions = extensions.get(file_format.lower(), [])
        if not supported_extensions:
            logger.error(f"Format {file_format} non supporté. Formats supportés: {', '.join(extensions.keys())}")
            return
        
        # Parcourir les fichiers du répertoire
        files_to_process = []
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    files_to_process.append(os.path.join(root, file))
        
        if not files_to_process:
            logger.error(f"Aucun fichier {file_format} trouvé dans {directory}")
            return
        
        logger.info(f"Trouvé {len(files_to_process)} fichiers à traiter.")
        
        # Charger les fichiers
        async with async_session() as session:
            for file_path in files_to_process:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    title = os.path.basename(file_path)
                    logger.info(f"Ajout du document: {title}")
                    
                    await rag_service.add_document(
                        db=session,
                        title=title,
                        content=content,
                        metadata={
                            "source": "file",
                            "path": file_path,
                            "type": file_format
                        }
                    )
                except Exception as e:
                    logger.error(f"Erreur lors du traitement du fichier {file_path}: {str(e)}")
            
            logger.info(f"✅ Chargement des documents terminé !")
    except Exception as e:
        logger.error(f"Erreur lors du chargement des documents: {str(e)}")


async def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Charge des documents dans la base de connaissances RAG')
    parser.add_argument('--input', type=str, help='Répertoire contenant les fichiers à charger')
    parser.add_argument('--format', type=str, default='markdown', 
                        choices=['markdown', 'text', 'html'], 
                        help='Format des fichiers à charger')
    parser.add_argument('--sample', action='store_true', help='Charger les documents d\'exemple')
    
    args = parser.parse_args()
    
    if args.sample:
        logger.info("Chargement des documents d'exemple...")
        await load_sample_documents()
    elif args.input:
        logger.info(f"Chargement des documents depuis {args.input} au format {args.format}...")
        await load_documents_from_files(args.input, args.format)
    else:
        logger.info("Aucune action spécifiée. Utilisation des documents d'exemple par défaut...")
        await load_sample_documents()


if __name__ == "__main__":
    asyncio.run(main()) 