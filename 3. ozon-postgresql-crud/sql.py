from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()

# Определение модели пользователя
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    age = Column(Integer)
    carts = relationship("Cart", back_populates="user")

# Определение модели товара
class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    carts = relationship("Cart", back_populates="product")

# Определение модели корзины
class Cart(Base):
    __tablename__ = 'carts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="carts")

# Функция для получения пользователя по имени
def get_user(session: sessionmaker, username: str) -> User:
    return session.query(User).filter(User.username == username).first()

# Функция для получения всех пользователей
def get_users_all(session: sessionmaker) -> list[User]:
    return session.query(User).all()

# Функция для создания нового пользователя
def create_user(session: sessionmaker, username: str, email: str, hashed_password: str, age: int) -> User:
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        age=age
    )
    session.add(new_user)
    session.commit()
    return new_user

# Функция для обновления информации о пользователе
def update_user(session: sessionmaker, user_id: int, username: str = None, email: str = None, hashed_password: str = None, age: int = None) -> User:
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        print("Пользователь не найден.")
        return None
    
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if hashed_password is not None:
        user.hashed_password = hashed_password
    if age is not None:
        user.age = age
    
    session.commit()
    return user

# Функция для получения всех товаров
def get_products_all(session: sessionmaker) -> list[Product]:
    return session.query(Product).all()

# Функция для создания нового товара
def create_product(session: sessionmaker, name: str, price: float) -> Product:
    new_product = Product(
        name=name,
        price=price
    )
    session.add(new_product)
    session.commit()
    return new_product

# Функция для обновления информации о товаре
def update_product(session: sessionmaker, product_id: int, name: str = None, price: float = None) -> Product:
    product = session.query(Product).filter(Product.id == product_id).first()
    if product is None:
        print("Товар не найден.")
        return None
    
    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    
    session.commit()
    return product

# Функция для добавления товара в корзину
def add_to_cart(session: sessionmaker, user_id: int, product_id: int, quantity: int = 1) -> Cart:
    new_cart_item = Cart(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity
    )
    session.add(new_cart_item)
    session.commit()
    return new_cart_item

# Функция для получения корзины пользователя
def get_cart(session: sessionmaker, user_id: int) -> list[Cart]:
    return session.query(Cart).filter(Cart.user_id == user_id).all()