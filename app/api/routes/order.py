from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User
from app.core.models import db_helper
from app.core.schemas.order import Order, OrderList
from app.core.security import get_current_user
from app.services import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])

order_service = OrderService()


@router.post(
    "/create",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.get_async_db)
):
    return await order_service.create_order_from_cart(session, user)


@router.get(
    "/my",
    response_model=list[Order],
)
async def get_my_orders(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.get_async_db),
):
    return await order_service.get_user_orders(session, user.id)


@router.get(
    "/{order_id}",
    response_model=Order,
)
async def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.get_async_db),
):
    order = await order_service.get_by_id(session, order_id)

    if order.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this order",
        )

    return order


@router.patch(
    "/{order_id}/status",
    response_model=Order,
)
async def update_status(
    order_id: int,
    new_status: str,
    session: AsyncSession = Depends(db_helper.get_async_db),
):
    return await order_service.update_status(session, order_id, new_status)
