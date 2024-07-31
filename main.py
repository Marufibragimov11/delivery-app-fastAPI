from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT

from auth_routes import auth_router
from order_routes import order_router
from product_routes import product_router
from schemas import Settings, LoginModel

app = FastAPI()
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(product_router)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
