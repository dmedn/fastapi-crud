from typing import Optional, Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Product, User
from app.repositories import ProductRepository, CategoryRepository, UserRepository
from app.services.base_service import BaseService


class ProductService(BaseService[Product]):
    """
    Service layer for managing products.
    Provides business logic for creation, updates, filtering, and cross-entity validation.
    """

    def __init__(self):
        """Initialize ProductService with associated repositories."""
        self.repository: ProductRepository = ProductRepository()
        super().__init__(self.repository)
        self.category_repo = CategoryRepository()
        self.user_repo = UserRepository()

    async def create_product(
            self,
            session: AsyncSession,
            seller_id: int,
            name: str,
            description: Optional[str],
            price: float,
            stock: int,
            category_id: int,
    ) -> Product:
        """
        Create a new product after validating the seller and category.
        Args:
            session (AsyncSession): Database session.
            seller_id (int): ID of the seller creating the product.
            name (str): Product name.
            description (Optional[str]): Product description.
            price (float): Product price.
            stock (int): Stock quantity.
            category_id (int): Category ID.
        Returns:
            Product: Created product instance.
        Raises:
            HTTPException: If seller or category is invalid or inactive.
        """
        seller = await self.user_repo.get_by_id(session, seller_id)
        if not seller or seller.role != "seller":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only active sellers can create products.",
            )
        category = await self.category_repo.get_by_id(session, category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive category.",
            )
        return await self.repository.create(
            session,
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            seller_id=seller_id,
        )

    async def update_product(
            self,
            session: AsyncSession,
            product_id: int,
            seller_id: int,
            data: dict,
    ) -> Product:
        """
        Update a product (only by its owner).
        Args:
            session (AsyncSession): Database session.
            product_id (int): ID of the product to update.
            seller_id (int): ID of the seller performing the update.
            data (dict): Fields to update.
        Returns:
            Product: Updated product instance.
        Raises:
            HTTPException: If product not found or seller mismatch.
        """
        product = await self.repository.get_by_id(session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=403, detail="You can only update your own products."
            )
        immutable_fields = {"id", "seller_id", "rating"}
        safe_data = {k: v for k, v in data.items() if k not in immutable_fields}

        updated_product = await self.repository.update(session, product_id, safe_data)
        return updated_product


    async def filter_products(
            self,
            session: AsyncSession,
            query: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            category_id: Optional[int] = None,
            sort_by: Optional[str] = None,
            limit: int = 20,
            offset: int = 0,
    ) -> Sequence[Product]:
        """Retrieve products based on filters (search, category, price, sorting)."""
        return await self.repository.filter_products(
            session=session,
            query=query,
            min_price=min_price,
            max_price=max_price,
            category_id=category_id,
            sort_by=sort_by,
            limit=limit,
            offset=offset,
        )

    async def get_top_rated(self, session: AsyncSession, limit: int = 10) -> Sequence[Product]:
        """Retrieve top-rated active products."""
        return await self.repository.get_top_rated(session, limit)

    async def get_users_with_product_in_cart(
            self, session: AsyncSession, product_id: int
    ) -> Sequence[User]:
        """
        Retrieve all users who have a specific product in their cart.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            product_id (int): ID of the product.
        Returns:
            Sequence[User]: List of users having this product in their cart.
        """
        cart_items = await self.repository.get_carts_with_product(session, product_id)
        user_ids = [item.user_id for item in cart_items]

        if not user_ids:
            return []

        result = await session.execute(
            self.user_repo.model.__table__.select().where(self.user_repo.model.id.in_(user_ids))
        )
        return result.scalars().all()
