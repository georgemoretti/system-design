import time
from pymongo import MongoClient
from passlib.context import CryptContext

# Настройка MongoDB
MONGO_URI = "mongodb://root:pass@mongo:27017/"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["shopdb"]
mongo_users_collection = mongo_db["users"]

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Загрузка тестовых данных
def load_test_data():
    # Проверка существования пользователя перед добавлением
    def add_user(username, email, hashed_password, age):
        user = mongo_users_collection.find_one({"username": username})
        if not user:
            user = {
                "username": username,
                "email": email,
                "hashed_password": hashed_password,
                "age": age,
            }
            mongo_users_collection.insert_one(user)

    # Создание мастер-пользователя
    add_user(
        username="admin",
        email="admin@example.com",
        hashed_password=pwd_context.hash("secret"),
        age=30,
    )

    # Создание тестовых пользователей
    add_user(
        username="user1",
        email="ivan.ivanov@example.com",
        hashed_password=pwd_context.hash("password1"),
        age=25,
    )

    add_user(
        username="user2",
        email="anna.petrova@example.com",
        hashed_password=pwd_context.hash("password2"),
        age=30,
    )

def wait_for_db(retries=10, delay=5):
    for _ in range(retries):
        try:
            mongo_client.admin.command('ismaster')
            print("Database is ready!")
            return
        except Exception as e:
            print(f"Database not ready yet: {e}")
            time.sleep(delay)
    raise Exception("Could not connect to the database")

if __name__ == "__main__":
    wait_for_db()
    load_test_data()