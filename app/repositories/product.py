from typing import Sequence, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Product, CartItem
from app.repositories.base_repo import BaseRepository




class ProductRepository(BaseRepository[Product]):
    """
    Repository for managing Product entities.

    Extends the BaseRepository to provide advanced functionality
    for working with product catalog features such as filtering,
    full-text search, category-based retrieval, and rating ranking.
    """

    def __init__(self):
        """Initialize the repository with the Product model."""
        super().__init__(Product)

    async def get_active_products(self, session: AsyncSession) -> Sequence[Product]:
        """
        Retrieve all active products (where `is_active` is True).
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
        Returns:
            Sequence[Product]: A list of active products.
        """
        result = await session.execute(
            select(self.model).where(self.model.is_active.is_(True))
        )
        return result.scalars().all()

    async def get_by_category(
            self, session: AsyncSession, category_id: int
    ) -> Sequence[Product]:
        """
        Retrieve all active products belonging to a specific category.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            category_id (int): ID of the category to filter by.
        Returns:
            Sequence[Product]: A list of products in the given category.
        """
        result = await session.execute(
            select(self.model).where(
                self.model.category_id == category_id,
                self.model.is_active.is_(True),
            )
        )
        return result.scalars().all()

    async def search_products(
            self,
            session: AsyncSession,
            query: str,
            limit: int = 20,
            offset: int = 0,
    ) -> Sequence[Product]:
        """
        Perform a full-text search across product names and descriptions.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            query (str): The search term (e.g., "gaming laptop").
            limit (int): Maximum number of results to return.
            offset (int): Number of records to skip for pagination.
        Returns:
            Sequence[Product]: A list of products matching the search query.
        """
        ts_query = func.plainto_tsquery("english", query)
        stmt = (
            select(self.model)
            .where(self.model.tsv.op("@@")(ts_query))
            .where(self.model.is_active.is_(True))
            .order_by(func.ts_rank_cd(self.model.tsv, ts_query).desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_top_rated(
            self, session: AsyncSession, limit: int = 10
    ) -> Sequence[Product]:
        """
        Retrieve top-rated active products.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            limit (int): Number of products to return.
        Returns:
            Sequence[Product]: A list of top-rated products.
        """
        result = await session.execute(
            select(self.model)
            .where(self.model.is_active.is_(True))
            .order_by(self.model.rating.desc())
            .limit(limit)
        )
        return result.scalars().all()

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
        """
        Retrieve products filtered by various parameters such as category,
        price range, and search query. Supports pagination and optional sorting.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            query (Optional[str]): Full-text search query.
            min_price (Optional[float]): Minimum product price.
            max_price (Optional[float]): Maximum product price.
            category_id (Optional[int]): Category filter.
            sort_by (Optional[str]): Sorting parameter ("price_asc", "price_desc", "rating").
            limit (int): Maximum number of records to return.
            offset (int): Number of records to skip (for pagination).
        Returns:
            Sequence[Product]: Filtered list of products.
        """
        stmt = select(self.model).where(self.model.is_active.is_(True))

        if category_id:
            stmt = stmt.where(self.model.category_id == category_id)
        if min_price is not None:
            stmt = stmt.where(self.model.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(self.model.price <= max_price)
        if query:
            ts_query = func.plainto_tsquery("english", query)
            stmt = stmt.where(self.model.tsv.op("@@")(ts_query))

        if sort_by == "price_asc":
            stmt = stmt.order_by(self.model.price.asc())
        elif sort_by == "price_desc":
            stmt = stmt.order_by(self.model.price.desc())
        elif sort_by == "rating":
            stmt = stmt.order_by(self.model.rating.desc())

        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_filtered(
            self,
            session: AsyncSession,
            query: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            category_id: Optional[int] = None,
    ) -> int:
        """
        Count the total number of products matching the given filters.
        Useful for pagination metadata.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            query (Optional[str]): Text query for full-text search.
            min_price (Optional[float]): Minimum product price.
            max_price (Optional[float]): Maximum product price.
            category_id (Optional[int]): Filter by category ID.
        Returns:
            int: Total count of filtered products.
        """
        stmt = select(func.count(self.model.id)).where(self.model.is_active.is_(True))

        if category_id:
            stmt = stmt.where(self.model.category_id == category_id)
        if min_price is not None:
            stmt = stmt.where(self.model.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(self.model.price <= max_price)
        if query:
            ts_query = func.plainto_tsquery("english", query)
            stmt = stmt.where(self.model.tsv.op("@@")(ts_query))

        result = await session.execute(stmt)
        return result.scalar_one()

    async def get_carts_with_product(self, session: AsyncSession, product_id: int) -> Sequence[CartItem]:
        """
        Retrieve all cart entries that contain a specific product.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            product_id (int): ID of the product to search for in carts.
        Returns:
            Sequence[CartItem]: A list of CartItem objects that reference the given product.
        """
        result = await session.execute(
            select(CartItem).where(CartItem.product_id == product_id)
        )
        return result.scalars().all()