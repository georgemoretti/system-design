import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ozon_jwt import Base, UserDB, ProductDB, CartDB, OrderDB
from passlib.context import CryptContext

# Настройка PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:archdb@db/ozon_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Загрузка тестовых данных
def load_test_data():
    db = SessionLocal()

    # Проверка существования пользователя перед добавлением
    def add_user(username, first_name, last_name, hashed_password, email):
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if not user:
            user = UserDB(
                username=username,
                first_name=first_name,
                last_name=last_name,
                hashed_password=hashed_password,
                email=email,
            )
            db.add(user)

    # Создание пользователей
    add_user(
        username="admin",
        first_name="Admin",
        last_name="Admin",
        hashed_password=pwd_context.hash("admin123"),
        email="admin@ozon.com",
    )

    add_user(
        username="user1",
        first_name="Ivan",
        last_name="Ivanov",
        hashed_password=pwd_context.hash("user123"),
        email="ivan.ivanov@ozon.com",
    )

    add_user(
        username="user2",
        first_name="Kirill",
        last_name="Kotov",
        hashed_password=pwd_context.hash("user456"),
        email="kirill.kotov@ozon.com",
    )

    # Создание продуктов
    def add_product(name, price, description, stock):
        product = db.query(ProductDB).filter(ProductDB.name == name).first()
        if not product:
            product = ProductDB(
                name=name,
                price=price,
                description=description,
                stock=stock,
            )
            db.add(product)

    add_product("Laptop", 999.99, "High-performance laptop", 10)
    add_product("Smartphone", 499.99, "Latest model smartphone", 20)
    add_product("Headphones", 149.99, "Noise-cancelling headphones", 30)

    # Создание корзин
    def add_cart(user_id):
        cart = db.query(CartDB).filter(CartDB.user_id == user_id).first()
        if not cart:
            cart = CartDB(user_id=user_id)
            db.add(cart)

    add_cart(1)  # admin
    add_cart(2)  # user1
    add_cart(3)  # user2

    # Создание заказов
    def add_order(user_id, total_price):
        order = db.query(OrderDB).filter(OrderDB.user_id == user_id, OrderDB.status == "pending").first()
        if not order:
            order = OrderDB(user_id=user_id, total_price=total_price, status="pending")
            db.add(order)

    add_order(1, 1499.99)  # admin
    add_order(2, 699.99)  # user1

    db.commit()
    db.close()


if __name__ == "__main__":
    load_test_data()
