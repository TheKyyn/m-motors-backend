from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, vehicles
from .config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API backend pour M-Motors - Location et vente de véhicules"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(auth.router)
app.include_router(vehicles.router)

@app.get("/")
async def root():
    """Route racine de l'API"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running"
    }
