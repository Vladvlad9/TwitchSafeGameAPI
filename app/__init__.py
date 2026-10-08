from app.routers.setup import include_routers
from app.middleware.cors_middleware import cors_middleware

__all__ = ['include_routers', 'cors_middleware']
