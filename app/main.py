from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from .routers import auth_router, vehicles_router, dossiers_router, admin_router, rag_router
from .config import settings
from .routes import rental_options_router

# Configuration des logs
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Middleware pour le logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.debug(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Une erreur interne est survenue"}
        )

# Inclusion des routers
app.include_router(auth_router)
app.include_router(vehicles_router)
app.include_router(dossiers_router)
app.include_router(admin_router)
app.include_router(rag_router)
app.include_router(
    rental_options_router,
    prefix="/api/v1",
    tags=["rental-options"]
)

@app.get("/")
async def root():
    """Route racine de l'API"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running"
    }
