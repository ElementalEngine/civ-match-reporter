from fastapi import APIRouter
from app.routes.upload import router as upload_router
from app.routes.matches import router as matches_router

router = APIRouter()
router.include_router(upload_router)
router.include_router(matches_router)