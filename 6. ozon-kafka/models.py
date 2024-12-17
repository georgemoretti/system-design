from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Pydantic models for request and response validation

class UserMongo(BaseModel):
    id: str
    username: str
    email: str
    hashed_password: str
    age: Optional[int] = None

class Product(BaseModel):
    id: int
    name: str
    price: float

class Cart(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

# SQLAlchemy models for the database

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    age = Column(Integer, nullable=True)

    carts = relationship("CartDB", back_populates="user")

class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)

    carts = relationship("CartDB", back_populates="product")

class CartDB(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    user = relationship("UserDB", back_populates="carts")
    product = relationship("ProductDB", back_populates="carts")
