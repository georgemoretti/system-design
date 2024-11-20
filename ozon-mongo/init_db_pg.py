import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ozon_jwt import Base, UserDB, ProductDB, CartDB

# Настройка PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://your_username:your_password@db:5432/shopdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Загрузка тестовых данных
def load_test_data():
    db = SessionLocal()

    # Проверка существования пользователя перед добавлением
    def add_user(username, email, hashed_password, age):
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if not user:
            user = UserDB(
                username=username,
                email=email,
                hashed_password=hashed_password,
                age=age,
            )
            db.add(user)

    # Проверка существования товара перед добавлением
    def add_product(name, price):
        product = db.query(ProductDB).filter(ProductDB.name == name).first()
        if not product:
            product = ProductDB(
                name=name,
                price=price,
            )
            db.add(product)

    # Проверка существования корзины перед добавлением
    def add_cart(user_id, product_id, quantity):
        cart = db.query(CartDB).filter(CartDB.user_id == user_id, CartDB.product_id == product_id).first()
        if not cart:
            cart = CartDB(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
            )
            db.add(cart)

    # Создание тестовых пользователей
    add_user(username="admin", email="admin@example.com", hashed_password="hashed_password", age=30)
    add_user(username="user1", email="ivan.ivanov@example.com", hashed_password="hashed_password1", age=25)
    add_user(username="user2", email="anna.petrova@example.com", hashed_password="hashed_password2", age=30)

    # Создание тестовых товаров
    add_product(name="Laptop", price=1200.00)
    add_product(name="Smartphone", price=800.00)
    add_product(name="Tablet", price=500.00)
    add_product(name="Headphones", price=200.00)

    # Создание тестовых корзин
    add_cart(user_id=1, product_id=1, quantity=1)  # admin, Laptop
    add_cart(user_id=2, product_id=2, quantity=2)  # user1, Smartphone
    add_cart(user_id=3, product_id=3, quantity=3)  # user2, Tablet

    db.commit()
    db.close()

def wait_for_db(retries=10, delay=5):
    for _ in range(retries):
        try:
            engine.connect()
            print("PostgreSQL is ready!")
            return
        except Exception as e:
            print(f"PostgreSQL not ready yet: {e}")
            time.sleep(delay)
    raise Exception("Could not connect to PostgreSQL")

if __name__ == "__main__":
    wait_for_db()
    load_test_data()