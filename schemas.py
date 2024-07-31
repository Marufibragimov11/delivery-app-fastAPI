from pydantic import BaseModel, validator
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    # @validator('email')
    # def validate_email(cls, v):
    #     if "@" not in v:
    #         raise ValueError("Must be a valid email address")
    #     return v

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'username': 'mohirdev',
                'email': 'mohirdev.praktikum@gmail.com',
                'password': 'password12345',
                'is_staff': False,
                'is_active': True
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = '8d1f898f4cd2f1da40599cc6dd6fc5ce93b905375265fe3eacc727c836ea26e0'


class LoginModel(BaseModel):
    username_or_email: str
    password: str


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_statuses: Optional[str] = "PENDING"
    user_id: Optional[int]
    product_id: int

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "quantity": 2,
            }
        }


class OrderStatusModel(BaseModel):
    order_statuses: Optional[str] = "PENDING"

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "order_statuses": "PENDING",
            }
        }


class ProductModel(BaseModel):
    id: Optional[int]
    name: str
    price: int

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "name": "Uzbek plov",
                "price": 30000
            }
        }
