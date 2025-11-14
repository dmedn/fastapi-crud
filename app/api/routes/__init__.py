from app.api.routes.product import router as product_router
from app.api.routes.category import router as category_router
from app.api.routes.review import router as review_router
from app.api.routes.user import router as user_router
from app.api.routes.cart import router as cart_router
from app.api.routes.order import router as order_router
__all__ = ["product_router", "category_router", "review_router", "user_router", "cart_router", "order_router"]