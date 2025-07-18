from fastapi import APIRouter
from .auth import auth_router
from .passport_data import passport_data_router
from .study_info import application_router
from .sms import sms_router
from .contract import report_router

api_router = APIRouter(prefix="/api")

api_router.include_router(sms_router)
api_router.include_router(auth_router)
api_router.include_router(passport_data_router)
api_router.include_router(application_router)
api_router.include_router(report_router)

