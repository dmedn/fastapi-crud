from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.models import User
from app.core.models.db_helper import db_helper
from app.core.schemas import Product, ProductCreate, ProductUpdate, ProductList
from app.core.security.roles import get_current_seller, get_current_user
from app.services import ProductService

router = APIRouter(prefix="/products", tags=["Products"])
product_service = ProductService()


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Create a new product. Only sellers can perform this action.",
)
async def create_product(
        product_data: ProductCreate,
        session: AsyncSession = Depends(db_helper.get_async_db),
        current_user: User = Depends(get_current_seller),
):
    """Endpoint to create a product."""
    return await product_service.create_product(
        session=session,
        seller_id=current_user.id,
        **product_data.model_dump(),
    )


@router.patch(
    "/{product_id}",
    response_model=Product,
    summary="Update a product",
    description="Update a product. Only the owner seller can update their product.",
)
async def update_product(
        product_id: int,
        product_data: ProductUpdate,
        session: AsyncSession = Depends(db_helper.get_async_db),
        current_user: User = Depends(get_current_seller),
):
    """Endpoint to update a product owned by the current seller."""
    return await product_service.update_product(
        session=session,
        product_id=product_id,
        seller_id=current_user.id,
        data=product_data.model_dump(exclude_unset=True),
    )


@router.get(
    "/",
    response_model=ProductList,
    summary="List products with filters",
    description="Retrieve a list of active products with optional filters such as price, category, and search query.",
)
async def list_products(
        session: AsyncSession = Depends(db_helper.get_async_db),
        query: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        category_id: Optional[int] = None,
        sort_by: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
):
    """Endpoint to retrieve filtered and paginated list of products."""
    products = await product_service.filter_products(
        session=session,
        query=query,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )
    total = await product_service.repository.count_filtered(
        session=session,
        query=query,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
    )
    return ProductList(total=total, items=products, page=offset // limit + 1, limit=limit)


@router.get(
    "/top",
    response_model=list[Product],
    summary="Get top-rated products",
    description="Retrieve a list of top-rated active products.",
)
async def get_top_rated_products(
        session: AsyncSession = Depends(db_helper.get_async_db),
        limit: int = 10,
):
    """Endpoint to get top-rated products."""
    return await product_service.get_top_rated(session, limit)


@router.get(
    "/{product_id}/cart-users",
    response_model=list[int],
    summary="Get users who have this product in their carts",
    description="Retrieve the list of user IDs who currently have this product in their shopping cart.",
)
async def get_users_with_product_in_cart(
        product_id: int,
        session: AsyncSession = Depends(db_helper.get_async_db),
        current_user: User = Depends(get_current_user),
):
    """Endpoint to get users who have added this product to their cart."""
    users = await product_service.get_users_with_product_in_cart(session, product_id)
    return [user.id for user in users]
