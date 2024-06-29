from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status, Request
from fastapi.responses import Response

from orders.orders_service.exceptions import OrderNotFoundError
from orders.orders_service.orders_service  import OrdersService
from orders.repository.orders_repository import OrdersRepository
from orders.repository.unit_of_work import UnitOfWork
from orders.web.app import app
from orders.web.api.schemas import (GetOrderSchema, GetOrdersSchema, CreateOrderSchema)

@app.get("/orders", response_model=GetOrdersSchema)
def get_orders(request: Request, cancelled: Optional[bool] = None, limit: Optional[int] = None):
    """ Get all the orders with cancelled orders """
    with UnitOfWork() as unit_of_work:
        repo = OrdersRepository(unit_of_work.session)
        orders_service = OrdersService(repo)
        results = orders_service.list_orders(limit=limit, cancelled=cancelled, user_id=request.state.user_id)
    
    return {'orders': [result.model_dump() for result in results]}


@app.post("/orders", status_code=status.HTTP_201_CREATED,response_model=GetOrderSchema)
def create_order(request: Request, payload: CreateOrderSchema):
    with UnitOfWork() as unit_of_work:
        repo = OrdersRepository(unit_of_work.session)
        orders_service = OrdersService(repo)
        order = payload.model_dump()['order']
        for item in order:
            item["size"] = item['size'].value
        order = orders_service.place_order(order, request.state.user_id)
        unit_of_work.commit()
        user_response = order.dict()
    return user_response


@app.get('/orders/{order_id}', response_model=GetOrderSchema)
def get_order(request: Request, order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = orders_service.get_order(order_id=order_id, user_id=request.state.user_id)
        user_response = order.dict()
        return user_response
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")

@app.put('/orders/{order_id}', response_model=GetOrderSchema)
def update_order(request: Request, order_id: UUID, payload: CreateOrderSchema):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            user_order = payload.model_dump()['order']
            for item in user_order:
                item['size'] = item['size'].value
            updated_order = orders_service.update_order(order_id=order_id, items=user_order, user_id=request.state.user_id)
            unit_of_work.commit()
        user_response = update_order.dict()
        return user_response
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail=f"Order with id: {order_id} not found")



@app.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_order(request: Request, order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            orders_service.delete_order(order_id=order_id, user_id=request.state.user_id)
            unit_of_work.commit()
        return
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )


@app.post("/orders/{order_id}/cancel", response_model=GetOrderSchema)
def cancel_order(request: Request, order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            cancel_order = orders_service.cancel_order(order_id=order_id, user_id=request.state.user_id)
            unit_of_work.commit()
            user_response = cancel_order.dict()
        return user_response
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )


@app.post("/orders/{order_id}/pay", response_model=GetOrderSchema)
def pay_order(request: Request, order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order_pay = orders_service.pay_order(order_id=order_id, user_id=request.state.user_id)
            unit_of_work.commit()
            user_response = order_pay.dict()
        return user_response
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Order with ID {order_id} not found"
        )

    