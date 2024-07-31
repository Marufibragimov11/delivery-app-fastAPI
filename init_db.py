from database import Base, engine
from models import User, Order, Product

Base.metadata.create_all(bind=engine)
