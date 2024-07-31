from fastapi import APIRouter
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from models import User, Product, Order
from schemas import OrderModel, OrderStatusModel
from database import session, engine

order_router = APIRouter(
    prefix='/order'
)

session = session(bind=engine)


@order_router.get('/')
async def welcome_page(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    return {'message': "Bu order route sahifasi"}


@order_router.post('/make', status_code=status.HTTP_201_CREATED)
async def make_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    new_order = Order(
        quantity=order.quantity,
        product_id=order.product_id
    )
    new_order.user = user
    session.add(new_order)
    session.commit()

    data = {
        "success": True,
        "code": 201,
        "message": "Order is created succussfully",
        "data": {
            "id": new_order.id,
            "quantity": new_order.quantity,
            "order_statuses": new_order.order_statuses.value,
            "total_price": new_order.quantity * new_order.product.price,
            "product": {
                "id": new_order.product.id,
                "name": new_order.product.name,
                "price": new_order.product.price
            }
        }
    }

    response = data

    return jsonable_encoder(response)


@order_router.get('/list', status_code=status.HTTP_200_OK)
async def list_all_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if user.is_staff:
        orders = session.query(Order).all()
        custom_data = [
            {
                "id": order.id,
                "quantity": order.quantity,
                "order_statuses": order.order_statuses.value,
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price
                },
                "total_price": order.quantity * order.product.price,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
            }
            for order in orders
        ]

        return jsonable_encoder(custom_data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin can see all orders")


@order_router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            custom_order = {
                "id": order.id,
                "product_id": order.product_id,
                "quantity": order.quantity,
                "order_statuses": order.order_statuses.value,
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price
                },
                "total_price": order.quantity * order.product.price,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
            }
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with {id} ID is not found")

        return jsonable_encoder(custom_order)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin is allowed to this request")


@order_router.get('/user/orders', status_code=status.HTTP_200_OK)
async def get_user_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    custom_data = [
        {
            "id": order.id,
            "quantity": order.quantity,
            "order_statuses": order.order_statuses.value,
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "total_price": order.quantity * order.product.price,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
        }
        for order in user.orders
    ]

    return jsonable_encoder(custom_data)


@order_router.get('/user/order/{id}', status_code=status.HTTP_200_OK)
async def get_user_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    order = session.query(Order).filter(Order.id == id, Order.user == current_user).first()
    if order:
        order_data = {
            "id": order.id,
            "quantity": order.quantity,
            "order_statuses": order.order_statuses.value,
            "total_price": order.quantity * order.product.price,
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
        }
        return jsonable_encoder(order_data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with this ID {id}")


@order_router.put('/{id}/update', status_code=status.HTTP_200_OK)
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    order_to_update = session.query(Order).filter(Order.id == id).first()
    if order_to_update.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can not update other user's order")

    order_to_update.quantity = order.quantity
    order_to_update.product_id = order.product_id

    session.commit()

    custom_response = {
        "success": True,
        "code": 200,
        "message": "Sizning buyurtmangiz muvaffaqiyatli o'zgartirildi",
        "data": {
            "id": order.id,
            "quantity": order.quantity,
            "product": order.product_id,
            "order_status": order.order_statuses
        }
    }

    return jsonable_encoder(custom_response)


@order_router.patch('/{id}/update-status', status_code=status.HTTP_200_OK)
async def update_order_status(id: int, order: OrderStatusModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    if user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == id).first()
        order_to_update.order_statuses = order.order_statuses
        session.commit()

        custom_response = {
            "success": True,
            "code": 200,
            "message": "User's order is updated successfully",
            "data": {
                "id": order_to_update.id,
                "order_status": order_to_update.order_statuses
            }
        }
        return jsonable_encoder(custom_response)


@order_router.delete('/{id}/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    order = session.query(Order).filter(Order.id == id).first()
    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can not delete other user's order")

    if order.order_statuses != "PENDING":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can not delete in_transit and delivered orders")

    session.delete(order)
    session.commit()
    custom_response = {
        "success": True,
        "code": 200,
        "message": "User's order is deleted successfully",
        "data": None
    }
    return jsonable_encoder(custom_response)
