from fastapi import APIRouter
from app.api.routes import product_router, category_router, review_router, cart_router,user_router

router = APIRouter()
router.include_router(product_router)
router.include_router(category_router)
router.include_router(review_router)
router.include_router(cart_router)
router.include_router(user_router)
