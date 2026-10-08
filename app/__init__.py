from app.routers.setup import include_routers
from app.middleware.cors_middleware import cors_middleware
from .app import get_application
from .lifespan import lifespan

__all__ = ['include_routers', 'cors_middleware', 'get_application', 'lifespan']
