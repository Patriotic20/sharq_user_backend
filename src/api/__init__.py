from fastapi import APIRouter
from .auth import auth_router
from .application import application_router

api_router = APIRouter(
    prefix="/api"
)

api_router.include_router(auth_router)
api_router.include_router(application_router)


