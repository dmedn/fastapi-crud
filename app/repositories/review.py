from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from app.core.models import Review, Product
from app.repositories import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    """
    Repository for managing Review entities.

    Extends the BaseRepository to include additional functionality
    such as calculating average product ratings, filtering reviews
    by user or product, and handling review activation/deactivation.
    """

    def __init__(self):
        """Initialize the repository with the Review model."""
        super().__init__(Review)

    async def get_by_user(
            self, session: AsyncSession, user_id: int
    ) -> Sequence[Review]:
        """
        Retrieve all reviews left by a specific user.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            user_id (int): ID of the user.
        Returns:
            Sequence[Review]: List of reviews written by the user.
        """
        result = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_product(
            self, session: AsyncSession, product_id: int
    ) -> Sequence[Review]:
        """
        Retrieve all active reviews for a specific product.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            product_id (int): ID of the product.
        Returns:
            Sequence[Review]: List of active reviews for the product.
        """
        result = await session.execute(
            select(self.model).where(
                self.model.product_id == product_id,
                self.model.is_active.is_(True),
            )
        )
        return result.scalars().all()

    async def get_average_rating(
            self, session: AsyncSession, product_id: int
    ) -> Optional[float]:
        """
        Calculate the average rating for a product based on active reviews.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            product_id (int): ID of the product.
        Returns:
            Optional[float]: Average rating value or None if no reviews exist.
        """
        stmt = select(func.avg(self.model.grade)).where(
            self.model.product_id == product_id,
            self.model.is_active.is_(True),
        )
        result = await session.execute(stmt)
        avg_rating = result.scalar_one_or_none()
        return float(avg_rating) if avg_rating is not None else None

    async def update_product_rating(
            self, session: AsyncSession, product_id: int
    ) -> None:
        """
        Recalculate and update the rating of a product
        based on its current active reviews.

        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            product_id (int): ID of the product.
        """
        avg_rating = await self.get_average_rating(session, product_id)
        if avg_rating is None:
            avg_rating = 0.0

        await session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(rating=avg_rating)
        )
        await session.commit()

    async def deactivate_review(
            self, session: AsyncSession, review_id: int
    ) -> Optional[Review]:
        """
        Deactivate a review (set `is_active = False`) instead of deleting it.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            review_id (int): ID of the review.
        Returns:
            Optional[Review]: The updated review object, or None if not found.
        """
        review = await session.get(self.model, review_id)
        if not review:
            return None

        review.is_active = False
        await session.commit()
        await session.refresh(review)

        # Recalculate product rating
        await self.update_product_rating(session, review.product_id)
        return review

    async def delete(
            self, session: AsyncSession, obj_id: int
    ) -> Optional[Review]:
        """
        Override delete method to ensure product rating
        is updated after a review is removed.
        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            obj_id (int): ID of the review to delete.
        Returns:
            Optional[Review]: The deleted review object, or None if not found.
        """
        review = await session.get(self.model, obj_id)
        if not review:
            return None

        product_id = review.product_id
        await session.delete(review)
        await session.commit()

        await self.update_product_rating(session, product_id)
        return review
