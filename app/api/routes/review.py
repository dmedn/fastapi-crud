from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import db_helper, User
from app.core.schemas import ReviewSchema, ReviewCreate
from app.core.security import get_current_user
from app.services import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])
review_service = ReviewService()


@router.post(
    "/",
    response_model=ReviewSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product review",
    description="Allows an authenticated user to leave a review for a specific product. "
                "Each user can leave only one review per product."
)
async def create_review(
    review_data: ReviewCreate,
    session: AsyncSession = Depends(db_helper.get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new review for a product."""
    return await review_service.create_review(
        session=session,
        user=current_user,
        product_id=review_data.product_id,
        grade=review_data.grade,
        comment=review_data.comment,
    )


@router.get(
    "/product/{product_id}",
    response_model=list[ReviewSchema],
    summary="Get all reviews for a specific product",
    description="Retrieve all reviews left by users for a given product."
)
async def get_reviews_for_product(
    product_id: int,
    session: AsyncSession = Depends(db_helper.get_async_db),
):
    """Fetch all reviews for a given product."""
    return await review_service.repository.get_reviews_for_product(session, product_id)


@router.put(
    "/{review_id}",
    response_model=ReviewSchema,
    summary="Update an existing review",
    description="Allows the author of a review to update their rating or comment."
)
async def update_review(
    review_id: int,
    review_data: ReviewCreate,
    session: AsyncSession = Depends(db_helper.get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user's existing review."""
    review = await review_service.get_by_id(session, review_id)
    if not review or review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews.",
        )

    updated_review = await review_service.update_review(
        session=session,
        review_id=review_id,
        user=current_user,
        grade=review_data.grade,
        comment=review_data.comment,
    )
    return updated_review


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a review",
    description="Allows a user to delete their own review. "
                "Admins can delete any review."
)
async def delete_review(
    review_id: int,
    session: AsyncSession = Depends(db_helper.get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a user's review."""
    review = await review_service.get_by_id(session, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if current_user.role != "admin" and review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can delete only your own reviews.",
        )

    await review_service.delete_review(session=session, review_id=review_id)
    return None
