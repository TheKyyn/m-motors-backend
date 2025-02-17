from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import vehicles, users, dossiers, rentals
from .database import engine
from .models import Base

app = FastAPI(title="M-Motors API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(vehicles.router, prefix="/api/v1", tags=["vehicles"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(dossiers.router, prefix="/api/v1", tags=["dossiers"])
app.include_router(rentals.router, prefix="/api/v1", tags=["rentals"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API M-Motors"}
