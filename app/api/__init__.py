from fastapi import APIRouter
from app.api.routes import product_router

router = APIRouter()
router.include_router(product_router)