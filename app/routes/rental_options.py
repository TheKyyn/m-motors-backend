from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models.rental_option import RentalOption
from ..schemas.rental_option import RentalOptionCreate, RentalOptionResponse
from ..database import get_db

router = APIRouter()

@router.post("/rental-options/", response_model=RentalOptionResponse)
def create_rental_option(
    option: RentalOptionCreate,
    db: Session = Depends(get_db)
):
    db_option = RentalOption(**option.dict())
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    return db_option

@router.get("/rental-options/", response_model=List[RentalOptionResponse])
def list_rental_options(
    db: Session = Depends(get_db)
):
    return db.query(RentalOption).all()

@router.put("/dossiers/{dossier_id}/rental-options/{option_id}")
def add_option_to_dossier(
    dossier_id: int,
    option_id: int,
    db: Session = Depends(get_db)
):
    dossier = db.query(Dossier).filter(Dossier.id == dossier_id).first()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")
        
    option = db.query(RentalOption).filter(RentalOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
        
    dossier.rental_options.append(option)
    db.commit()
    return {"status": "success"} 