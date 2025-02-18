from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models.vehicle import Vehicle
from ..schemas.vehicle import (
    VehicleCreate, VehicleResponse, VehicleUpdate,
    VehicleFilter
)
from ..security import get_current_active_user, get_current_admin_user
from ..models.user import User
from ..services.s3 import s3_service
from ..config import settings

router = APIRouter(prefix="/vehicles", tags=["Véhicules"])

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Crée un nouveau véhicule (admin uniquement)"""
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle

@router.get("/", response_model=List[VehicleResponse])
async def list_vehicles(
    filter: VehicleFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Liste tous les véhicules avec filtres optionnels"""
    query = select(Vehicle)
    
    if filter.brand:
        query = query.where(Vehicle.brand.ilike(f"%{filter.brand}%"))
    if filter.model:
        query = query.where(Vehicle.model.ilike(f"%{filter.model}%"))
    if filter.min_year:
        query = query.where(Vehicle.year >= filter.min_year)
    if filter.max_year:
        query = query.where(Vehicle.year <= filter.max_year)
    if filter.min_price:
        query = query.where(Vehicle.price >= filter.min_price)
    if filter.max_price:
        query = query.where(Vehicle.price <= filter.max_price)
    if filter.fuel_type:
        query = query.where(Vehicle.fuel_type == filter.fuel_type)
    if filter.transmission:
        query = query.where(Vehicle.transmission == filter.transmission)
    if filter.available_for_sale is not None:
        query = query.where(Vehicle.is_available_for_sale == filter.available_for_sale)
    if filter.available_for_rent is not None:
        query = query.where(Vehicle.is_available_for_rent == filter.available_for_rent)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_db)):
    """Récupère un véhicule par son ID"""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    return vehicle

@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_update: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Met à jour un véhicule (admin uniquement)"""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    
    for field, value in vehicle_update.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    
    await db.commit()
    await db.refresh(vehicle)
    return vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprime un véhicule (admin uniquement)"""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    
    await db.delete(vehicle)
    await db.commit()
    return None

@router.post("/{vehicle_id}/images", response_model=dict)
async def upload_vehicle_image(
    vehicle_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Upload une image pour un véhicule (admin uniquement)"""
    # Vérifier que le véhicule existe
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé"
        )
    
    # Vérifier le type de fichier
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être une image"
        )
    
    try:
        # Upload l'image vers S3
        image_url = await s3_service.upload_file(
            file=file,
            prefix=settings.S3_VEHICLES_PREFIX
        )
        
        # Mettre à jour le véhicule avec l'URL de l'image
        if not vehicle.images:
            vehicle.images = []
        vehicle.images.append(image_url)
        await db.commit()
        
        return {"url": image_url}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload de l'image: {str(e)}"
        ) 