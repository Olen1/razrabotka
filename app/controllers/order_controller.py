# app/controllers/order_controller.py
from typing import List
from litestar import Controller, get, post, put, delete
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from sqlalchemy.ext.asyncio import AsyncSession

from app.User_schem import OrderCreate, OrderUpdate, OrderResponse, OrdersListResponse
from app.services.order_service import OrderService


class OrderController(Controller):
    path = "/orders"

    @post("/")
    async def create_order(
            self,
            order_service: OrderService,
            session: AsyncSession,
            order_data: OrderCreate
    ) -> OrderResponse:
        order = await order_service.create_order(session, order_data)
        return OrderResponse.model_validate(order)

    @get("/{order_id:str}")
    async def get_order_by_id(
            self,
            order_service: OrderService,
            session: AsyncSession,
            order_id: str
    ) -> OrderResponse:
        order = await order_service.get_order_by_id(session, order_id)
        if not order:
            raise NotFoundException(detail=f"Order with ID {order_id} not found")
        return OrderResponse.model_validate(order)

    @get("/")
    async def get_orders(
            self,
            order_service: OrderService,
            session: AsyncSession,
            count: int = Parameter(default=10, ge=1, le=100),
            page: int = Parameter(default=1, ge=1)
    ) -> OrdersListResponse:
        orders = await order_service.get_orders_by_filter(session, count=count, page=page)
        total_count = await order_service.get_total_orders_count(session)
        return OrdersListResponse(
            orders=[OrderResponse.model_validate(order) for order in orders],
            total_count=total_count
        )

    @put("/{order_id:str}")
    async def update_order(
            self,
            order_service: OrderService,
            session: AsyncSession,
            order_id: str,
            order_data: OrderUpdate
    ) -> OrderResponse:
        order = await order_service.update_order(session, order_id, order_data)
        return OrderResponse.model_validate(order)

    @delete("/{order_id:str}")
    async def delete_order(
            self,
            order_service: OrderService,
            session: AsyncSession,
            order_id: str
    ) -> None:
        await order_service.delete_order(session, order_id)