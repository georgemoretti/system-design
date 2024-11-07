from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Подключение к PostgreSQL
DATABASE_URL = "postgresql+psycopg2://your_username:your_password@localhost/shopdb"
engine = create_engine(DATABASE_URL)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# Модели данных для SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    age = Column(Integer, nullable=True)
    carts = relationship("Cart", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    carts = relationship("Cart", back_populates="product")

class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="carts")

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Зависимости для получения текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    db = SessionLocal()
    user = db.query(User).filter(User.username == form_data.username).first()
    db.close()

    if user and pwd_context.verify(form_data.password, user.hashed_password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# GET /users - Получить всех пользователей (требует аутентификации)
@app.get("/users", response_model=List[User])
def get_users(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

# POST /users - Создать нового пользователя (требует аутентификации)
@app.post("/users", response_model=User)
def create_user(user: User, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    hashed_password = pwd_context.hash(user.hashed_password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password, age=user.age)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

# PUT /users/{user_id} - Обновить информацию о пользователе (требует аутентификации)
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.username = updated_user.username
        db_user.email = updated_user.email
        db_user.hashed_password = pwd_context.hash(updated_user.hashed_password)
        db_user.age = updated_user.age
        db.commit()
        db.refresh(db_user)
        db.close()
        return db_user
    db.close()
    raise HTTPException(status_code=404, detail="User not found")

# GET /products - Получить список товаров (требует аутентификации)
@app.get("/products", response_model=List[Product])
def get_products(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

# POST /products - Создать новый товар (требует аутентификации)
@app.post("/products", response_model=Product)
def create_product(product: Product, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    db_product = Product(name=product.name, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

# PUT /products/{product_id} - Обновить информацию о товаре (требует аутентификации)
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_product: Product, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db_product.name = updated_product.name
        db_product.price = updated_product.price
        db.commit()
        db.refresh(db_product)
        db.close()
        return db_product
    db.close()
    raise HTTPException(status_code=404, detail="Product not found")

# POST /carts - Добавить товар в корзину (требует аутентификации)
@app.post("/carts", response_model=Cart)
def add_to_cart(user_id: int, product_id: int, quantity: int = 1, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    db_cart = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    db.close()
    return db_cart

# GET /carts/{user_id} - Получить корзину пользователя (требует аутентификации)
@app.get("/carts/{user_id}", response_model=List[Cart])
def get_cart(user_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    db.close()
    return cart_items

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)