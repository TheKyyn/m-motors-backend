from .auth import router as auth_router
from .vehicles import router as vehicles_router
from .dossiers import router as dossiers_router
from .admin import router as admin_router

__all__ = ["auth_router", "vehicles_router", "dossiers_router", "admin_router"] 