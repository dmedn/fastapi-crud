from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import db_helper, User
from app.core.schemas.cart import Cart, CartItem, CartItemCreate, CartItemUpdate
from app.core.security.dependencies import get_current_user
from app.services import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])

cart_service = CartService()


@router.get("/", response_model=Cart)
async def get_user_cart(
    session: AsyncSession = Depends(db_helper.get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve the current user's cart.
    Returns all items along with total quantity and total price.
    """
    return await cart_service.get_user_cart(session,current_user)


@router.post("/", response_model=CartItem, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_data: CartItemCreate,
    session: AsyncSession = Depends(db_helper.get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a product to the user's cart.
    If the product already exists in the cart, its quantity will be updated.
    """
    return await cart_service.add_to_cart(
        session=session,
        user=current_user,
        product_id=item_data.product_id,
        quantity=item_data.quantity,
    )


@router.patch("/{product_id}", response_model=CartItem)
async def update_cart_item(
    product_id: int,
    data: CartItemUpdate,
    session: AsyncSession = Depends(db_helper.get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the quantity of an existing product in the cart.
    """
    updated_item = await cart_service.update_quantity(
        session=session,
        user=current_user,
        product_id=product_id,
        quantity=data.quantity,
    )
    if not updated_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return updated_item


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    product_id: int,
    session: AsyncSession = Depends(db_helper.get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove a specific product from the user's cart.
    """
    deleted = await cart_service.remove_from_cart(
        session=session,
        user=current_user,
        product_id=product_id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"detail": "Item removed successfully"}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    session: AsyncSession = Depends(db_helper.get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Clear all items from the current user's cart.
    """
    await cart_service.clear_cart(session=session, user=current_user)
    return {"detail": "Cart cleared successfully"}
