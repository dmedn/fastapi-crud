from app.api.routes.product import router as product_router
from app.api.routes.category import router as category_router
from app.api.routes.review import router as review_router
from app.api.routes.user import router as user_router
__all__ = ["product_router", "category_router", "review_router", "user_router"]