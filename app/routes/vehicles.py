from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.vehicle import Vehicle
from ..schemas.vehicle import VehicleCreate, VehicleResponse
from ..database import get_db

router = APIRouter()

@router.get("/vehicles/", response_model=List[VehicleResponse])
def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    for_sale: Optional[bool] = None,
    for_rent: Optional[bool] = None,
    brand: Optional[str] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Vehicle)
    
    if for_sale is not None:
        query = query.filter(Vehicle.is_available_for_sale == for_sale)
    if for_rent is not None:
        query = query.filter(Vehicle.is_available_for_rent == for_rent)
    if brand:
        query = query.filter(Vehicle.brand.ilike(f"%{brand}%"))
    if max_price:
        query = query.filter(Vehicle.price <= max_price)
        
    vehicles = query.offset(skip).limit(limit).all()
    return vehicles

@router.put("/vehicles/{vehicle_id}/toggle-availability")
def toggle_vehicle_availability(
    vehicle_id: int,
    for_sale: Optional[bool] = None,
    for_rent: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
        
    if for_sale is not None:
        vehicle.is_available_for_sale = for_sale
    if for_rent is not None:
        vehicle.is_available_for_rent = for_rent
        
    db.commit()
    return {"status": "success"}