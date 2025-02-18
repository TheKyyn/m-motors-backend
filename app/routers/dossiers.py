from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
import json

from ..database import get_db
from ..models import User, Dossier, Vehicle
from ..schemas import (
    DossierCreate, DossierResponse, DossierUpdate, 
    DossierFilter, Document, DossierStatus, DossierType
)
from ..security import get_current_active_user, get_current_admin_user

router = APIRouter(prefix="/dossiers", tags=["Dossiers"])

@router.post("/", response_model=DossierResponse, status_code=status.HTTP_201_CREATED)
async def create_dossier(
    dossier: DossierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crée un nouveau dossier"""
    # Vérifier si le véhicule existe et est disponible
    vehicle = await db.execute(
        select(Vehicle).where(
            and_(
                Vehicle.id == dossier.vehicle_id,
                Vehicle.is_available_for_sale if dossier.type == DossierType.ACHAT else Vehicle.is_available_for_rent
            )
        )
    )
    if not vehicle.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé ou non disponible pour ce type de transaction"
        )
    
    # Vérifier si l'utilisateur n'a pas déjà un dossier en cours pour ce véhicule
    existing_dossier = await db.execute(
        select(Dossier).where(
            and_(
                Dossier.user_id == current_user.id,
                Dossier.vehicle_id == dossier.vehicle_id,
                Dossier.status.in_([
                    DossierStatus.EN_ATTENTE.value,
                    DossierStatus.EN_COURS_DE_TRAITEMENT.value
                ])
            )
        )
    )
    if existing_dossier.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un dossier est déjà en cours pour ce véhicule"
        )
    
    # Créer le dossier
    db_dossier = Dossier(
        user_id=current_user.id,
        **dossier.model_dump()
    )
    
    db.add(db_dossier)
    await db.commit()
    await db.refresh(db_dossier)
    return db_dossier

@router.get("/", response_model=List[DossierResponse])
async def list_dossiers(
    filter: DossierFilter = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Liste tous les dossiers (admin uniquement)"""
    query = select(Dossier)
    
    if filter.type:
        query = query.where(Dossier.type == filter.type)
    if filter.status:
        query = query.where(Dossier.status == filter.status)
    if filter.vehicle_id:
        query = query.where(Dossier.vehicle_id == filter.vehicle_id)
    if filter.user_id:
        query = query.where(Dossier.user_id == filter.user_id)
    if filter.created_after:
        query = query.where(Dossier.created_at >= filter.created_after)
    if filter.created_before:
        query = query.where(Dossier.created_at <= filter.created_before)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/me", response_model=List[DossierResponse])
async def list_my_dossiers(
    status: Optional[DossierStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Liste les dossiers de l'utilisateur connecté"""
    query = select(Dossier).where(Dossier.user_id == current_user.id)
    
    if status:
        query = query.where(Dossier.status == status.value)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{dossier_id}", response_model=DossierResponse)
async def get_dossier(
    dossier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère les détails d'un dossier"""
    query = select(Dossier).where(Dossier.id == dossier_id)
    
    if not current_user.is_admin:
        query = query.where(Dossier.user_id == current_user.id)
    
    result = await db.execute(query)
    dossier = result.scalar_one_or_none()
    
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dossier non trouvé"
        )
    return dossier

@router.patch("/{dossier_id}", response_model=DossierResponse)
async def update_dossier(
    dossier_id: int,
    dossier_update: DossierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Met à jour un dossier"""
    query = select(Dossier).where(Dossier.id == dossier_id)
    
    if not current_user.is_admin:
        query = query.where(Dossier.user_id == current_user.id)
        
        # Vérifier que le dossier n'est pas dans un état final
        result = await db.execute(query)
        dossier = result.scalar_one_or_none()
        if dossier and dossier.status in [
            DossierStatus.ACCEPTE.value,
            DossierStatus.REFUSE.value,
            DossierStatus.ANNULE.value
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le dossier ne peut plus être modifié"
            )
    
    result = await db.execute(query)
    dossier = result.scalar_one_or_none()
    
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dossier non trouvé"
        )
    
    # Mise à jour des champs autorisés
    update_data = dossier_update.model_dump(exclude_unset=True)
    if not current_user.is_admin:
        # Supprimer les champs réservés aux admins
        update_data.pop('status', None)
        update_data.pop('admin_comments', None)
    
    for field, value in update_data.items():
        setattr(dossier, field, value)
    
    await db.commit()
    await db.refresh(dossier)
    return dossier

@router.post("/{dossier_id}/documents", response_model=DossierResponse)
async def add_document(
    dossier_id: int,
    document_type: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Ajoute un document à un dossier"""
    # Vérifier l'accès au dossier
    query = select(Dossier).where(Dossier.id == dossier_id)
    if not current_user.is_admin:
        query = query.where(Dossier.user_id == current_user.id)
    
    result = await db.execute(query)
    dossier = result.scalar_one_or_none()
    
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dossier non trouvé"
        )
    
    # TODO: Implémenter le stockage du fichier sur S3
    # Pour l'instant, on simule l'ajout du document
    new_document = Document(
        name=file.filename,
        type=document_type,
        url=f"https://example.com/{file.filename}",
        uploaded_at=datetime.utcnow(),
        status="en_attente"
    )
    
    # Mettre à jour la liste des documents
    documents = dossier.documents or []
    documents.append(new_document.model_dump())
    dossier.documents = documents
    
    await db.commit()
    await db.refresh(dossier)
    return dossier

@router.delete("/{dossier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_dossier(
    dossier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Annule un dossier"""
    query = select(Dossier).where(Dossier.id == dossier_id)
    if not current_user.is_admin:
        query = query.where(Dossier.user_id == current_user.id)
    
    result = await db.execute(query)
    dossier = result.scalar_one_or_none()
    
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dossier non trouvé"
        )
    
    if dossier.status in [DossierStatus.ACCEPTE.value, DossierStatus.REFUSE.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le dossier ne peut plus être annulé"
        )
    
    dossier.status = DossierStatus.ANNULE.value
    await db.commit()
    return None 