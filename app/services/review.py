from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.core.models import Review, Product, User
from app.repositories import ReviewRepository, ProductRepository
from app.services.base_service import BaseService


class ReviewService(BaseService[Review]):
    """
    Service layer for managing product reviews.
    Provides business logic for creating, updating, deleting, and
    recalculating product ratings based on user reviews.
    """

    def __init__(self):
        """Initialize ReviewService with associated repositories."""
        self.repository: ReviewRepository = ReviewRepository()
        super().__init__(self.repository)
        self.product_repo = ProductRepository()

    async def get_reviews_for_product(
        self, session: AsyncSession, product_id: int
    ) -> Sequence[Review]:
        """
        Retrieve all reviews for a specific product.
        Args:
            session (AsyncSession): Database session.
            product_id (int): ID of the product.
        Returns:
            Sequence[Review]: List of reviews associated with the product.
        """
        return await self.repository.get_reviews_for_product(session, product_id)

    async def get_reviews_by_user(
        self, session: AsyncSession, user_id: int
    ) -> Sequence[Review]:
        """
        Retrieve all reviews created by a specific user.
        Args:
            session (AsyncSession): Database session.
            user_id (int): ID of the user.
        Returns:
            Sequence[Review]: List of reviews created by the given user.
        """
        return await self.repository.get_by_user(session, user_id)

    async def create_review(
        self,
        session: AsyncSession,
        user: User,
        product_id: int,
        grade: int,
        comment: Optional[str] = None,
    ) -> Review:
        """
        Create a new review for a product.
        Args:
            session (AsyncSession): Database session.
            user (User): Authenticated user creating the review.
            product_id (int): ID of the reviewed product.
            grade (int): Review rating (1–5).
            comment (Optional[str]): Review comment.
        Returns:
            Review: Created review instance.
        Raises:
            HTTPException: If user has already reviewed the product.
        """
        existing = await self.repository.get_user_review_for_product(session, user.id, product_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has already reviewed this product.",
            )

        review = await self.repository.create(
            session,
            user_id=user.id,
            product_id=product_id,
            grade=grade,
            comment=comment,
        )

        await self._recalculate_product_rating(session, product_id)
        return review

    async def update_review(
        self,
        session: AsyncSession,
        review_id: int,
        user: User,
        grade: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> Review:
        """
        Update an existing review (only by its author).
        Args:
            session (AsyncSession): Database session.
            review_id (int): ID of the review to update.
            user (User): Authenticated user performing the update.
            grade (Optional[int]): New grade value (1–5).
            comment (Optional[str]): Updated review comment.
        Returns:
            Review: Updated review instance.
        Raises:
            HTTPException: If review not found or user lacks permissions.
        """
        review = await self.repository.get_by_id(session, review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

        if review.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        data = {}
        if grade is not None:
            data["grade"] = grade
        if comment is not None:
            data["comment"] = comment

        updated = await self.repository.update(session, review_id, data)
        await self._recalculate_product_rating(session, review.product_id)
        return updated

    async def delete_review(
        self,
        session: AsyncSession,
        review_id: int,
        user: User,
    ) -> None:
        """
        Delete a review (only by its author or an admin).
        Args:
            session (AsyncSession): Database session.
            review_id (int): ID of the review to delete.
            user (User): Authenticated user performing the deletion.
        Raises:
            HTTPException: If review not found or access is forbidden.
        """
        review = await self.repository.get_by_id(session, review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

        if user.role != "admin" and review.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        await self.repository.delete(session, review_id)
        await self._recalculate_product_rating(session, review.product_id)


    async def _recalculate_product_rating(self, session: AsyncSession, product_id: int) -> None:
        """
        Recalculate and update the average rating for a given product.
        Args:
            session (AsyncSession): SQLAlchemy async session.
            product_id (int): ID of the product whose rating needs recalculation.
        Raises:
            HTTPException: If the product does not exist.
        """
        product = await self.product_repo.get_by_id(session, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found while recalculating rating.",
            )


        result = await session.execute(
            select(func.avg(Review.grade)).where(Review.product_id == product_id)
        )
        avg_rating = result.scalar() or 0.0

        product.rating = round(avg_rating, 2)
        await session.commit()
        await session.refresh(product)
