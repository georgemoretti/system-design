from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pymongo import MongoClient
from bson import ObjectId
import redis
import os
import json 

# Настройка PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:archdb@db/ozon"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Настройка Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://cache:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Подключение к MongoDB
MONGO_URI = "mongodb://root:pass@mongo:27017/"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["shopdb"]
mongo_users_collection = mongo_db["users"]

# Модели данных
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

# SQLAlchemy models
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

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Зависимости для получения текущего пользователя
async def get_current_client(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        else:
            return username
    except JWTError:
        raise credentials_exception

# Создание и проверка JWT токенов
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Маршрут для получения токена
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = mongo_users_collection.find_one({"username": form_data.username})

    if user and pwd_context.verify(form_data.password, user["hashed_password"]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Создание нового пользователя
@app.post("/users", response_model=UserMongo)
def create_user(user: UserMongo, current_user: str = Depends(get_current_client)):
    user_dict = user.dict()
    user_dict["hashed_password"] = pwd_context.hash(user_dict["hashed_password"])
    user_id = mongo_users_collection.insert_one(user_dict).inserted_id
    user_dict["id"] = str(user_id)
    return user_dict

# Поиск пользователя по логину
@app.get("/users/{username}", response_model=UserMongo)
def get_user_by_username(username: str, current_user: str = Depends(get_current_client)):
    user = mongo_users_collection.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

# Поиск пользователя по маске имени и фамилии
@app.get("/users", response_model=List[UserMongo])
def search_users_by_name(
    first_name: str, last_name: str, current_user: str = Depends(get_current_client)
):
    users = list(mongo_users_collection.find({"first_name": {"$regex": first_name, "$options": "i"}, "last_name": {"$regex": last_name, "$options": "i"}}))
    for user in users:
        user["id"] = str(user["_id"])
    return users

# Зависимости для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создание товара
@app.post("/products", response_model=Product)
def create_product(product: Product, db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    db_product = ProductDB(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Обновление кеша
    cache_key = "products"
    products = db.query(ProductDB).all()
    redis_client.set(cache_key, json.dumps([product.dict() for product in products]))

    return product

# Получение списка товаров
@app.get("/products", response_model=List[Product])
def get_products(db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    cache_key = "products"
    cached_products = redis_client.get(cache_key)

    if cached_products:
        return [Product(**product) for product in json.loads(cached_products)]

    products = db.query(ProductDB).all()
    if products:
        redis_client.set(cache_key, json.dumps([product.dict() for product in products]))

    return products

# Добавление товара в корзину
@app.post("/carts", response_model=Cart)
def add_to_cart(cart: Cart, db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    db_cart = CartDB(**cart.dict())
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return cart

# Получение корзины пользователя
@app.get("/carts/{user_id}", response_model=List[Cart])
def get_cart(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_client)):
    carts = db.query(CartDB).filter(CartDB.user_id == user_id).all()
    return carts

# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)