from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..models.dossier import Dossier
from ..schemas.dossier import DossierCreate, DossierResponse
from ..database import SessionLocal
import shutil
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/dossiers/", response_model=DossierResponse)
def create_dossier(dossier: DossierCreate, db: Session = Depends(get_db)):
    db_dossier = Dossier(**dossier.dict())
    db.add(db_dossier)
    db.commit()
    db.refresh(db_dossier)
    return db_dossier

@router.post("/dossiers/upload-documents/")
async def upload_documents(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "file_path": file_path}