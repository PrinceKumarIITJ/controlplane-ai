from fastapi import APIRouter
from app.api.govern import router as govern_router
from app.api.review import router as review_router
from app.api.audit import router as audit_router
from app.api.metrics import router as metrics_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(govern_router)
api_router.include_router(review_router)
api_router.include_router(audit_router)
api_router.include_router(metrics_router)
