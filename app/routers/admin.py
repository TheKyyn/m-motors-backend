from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import User, Dossier, Vehicle, RentalService
from ..schemas.dossier import DossierStatus, DossierResponse, DossierFilter
from ..schemas.rental_services import (
    ServiceCreate, ServiceUpdate, ServiceResponse,
    ServiceFilter, ServiceStatus
)
from ..security import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.patch("/dossiers/{dossier_id}/status", response_model=DossierResponse)
async def update_dossier_status(
    dossier_id: int,
    new_status: DossierStatus = Body(...),
    admin_comments: Optional[str] = Body(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Mise à jour du statut d'un dossier par un administrateur"""
    result = await db.execute(
        select(Dossier).where(Dossier.id == dossier_id)
    )
    dossier = result.scalar_one_or_none()
    
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dossier non trouvé"
        )
    
    # Vérifier les transitions de statut valides
    if dossier.status in [DossierStatus.ACCEPTE, DossierStatus.REFUSE, DossierStatus.ANNULE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le dossier ne peut plus être modifié"
        )
    
    dossier.status = new_status
    if admin_comments:
        dossier.admin_comments = admin_comments
    
    await db.commit()
    await db.refresh(dossier)
    return dossier

@router.get("/dossiers/pending", response_model=List[DossierResponse])
async def list_pending_dossiers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Liste tous les dossiers en attente de traitement"""
    result = await db.execute(
        select(Dossier).where(Dossier.status == DossierStatus.EN_ATTENTE)
    )
    dossiers = result.scalars().all()
    return list(dossiers)

@router.post("/dossiers/{dossier_id}/request-documents", response_model=DossierResponse)
async def request_additional_documents(
    dossier_id: int,
    document_types: List[str] = Body(...),
    message: str = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Demande de documents supplémentaires"""
    result = await db.execute(
        select(Dossier).where(Dossier.id == dossier_id)
    )
    dossier = result.scalar_one_or_none()
    
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dossier non trouvé"
        )
    
    # Mettre à jour le statut et ajouter un commentaire
    dossier.status = DossierStatus.DOCUMENTS_MANQUANTS
    dossier.admin_comments = f"{dossier.admin_comments or ''}\n[{datetime.utcnow()}] Documents requis : {', '.join(document_types)}\nMessage : {message}"
    
    await db.commit()
    await db.refresh(dossier)
    return dossier

@router.get("/dossiers/in-progress", response_model=List[DossierResponse])
async def list_in_progress_dossiers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Liste tous les dossiers en cours de traitement"""
    result = await db.execute(
        select(Dossier).where(
            Dossier.status.in_([
                DossierStatus.EN_COURS_DE_TRAITEMENT,
                DossierStatus.DOCUMENTS_MANQUANTS
            ])
        )
    )
    dossiers = result.scalars().all()
    return list(dossiers)

@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Crée un nouveau service de location"""
    db_service = RentalService(**service.model_dump())
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service

@router.get("/services", response_model=List[ServiceResponse])
async def list_services(
    filter: ServiceFilter = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Liste tous les services de location avec filtres optionnels"""
    query = select(RentalService)
    
    if filter.type:
        query = query.where(RentalService.type == filter.type)
    if filter.status:
        query = query.where(RentalService.status == filter.status)
    if filter.is_mandatory is not None:
        query = query.where(RentalService.is_mandatory == filter.is_mandatory)
    if filter.max_price_per_month:
        query = query.where(RentalService.price_per_month <= filter.max_price_per_month)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Récupère les détails d'un service"""
    result = await db.execute(
        select(RentalService).where(RentalService.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé"
        )
    return service

@router.patch("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Met à jour un service"""
    result = await db.execute(
        select(RentalService).where(RentalService.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé"
        )
    
    for field, value in service_update.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    
    await db.commit()
    await db.refresh(service)
    return service

@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprime un service"""
    result = await db.execute(
        select(RentalService).where(RentalService.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service non trouvé"
        )
    
    await db.delete(service)
    await db.commit()
    return None 