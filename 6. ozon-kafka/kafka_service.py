from kafka import KafkaProducer, KafkaConsumer
import json
from time import sleep
from redis import Redis
from sqlalchemy.orm import Session
from models import ProductDB, CartDB

# Настройка Kafka
KAFKA_BOOTSTRAP_SERVERS = "kafka1:9092"
KAFKA_TOPIC = "routes"

# Настройка Redis
REDIS_URL = "redis://cache:6379/0"
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

# Пример Kafka Producer для отправки данных
def send_to_kafka(message: dict):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send(KAFKA_TOPIC, value=message)
    producer.flush()

# Пример Kafka Consumer для получения данных
def consume_from_kafka():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',  # Начинать с самого первого сообщения
        enable_auto_commit=True,
        group_id="consumer_group"
    )

    for message in consumer:
        print(f"Received message: {message.value}")
        # Обработка сообщения, например, обновление Redis кэша или базы данных
        process_kafka_message(message.value)

# Обработка сообщения из Kafka
def process_kafka_message(message: dict):
    if message.get('action') == 'add_product_to_cart':
        add_product_to_cart(message['user_id'], message['product_id'], message['quantity'])

# Пример функции для добавления товара в корзину в базе данных
def add_product_to_cart(user_id: int, product_id: int, quantity: int, db: Session):
    cart_item = db.query(CartDB).filter(CartDB.user_id == user_id, CartDB.product_id == product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartDB(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(cart_item)
    db.commit()

# Пример функции для обновления Redis кэша с продукцией
def update_product_cache(db: Session):
    products = db.query(ProductDB).all()
    products_data = [{"id": product.id, "name": product.name, "price": product.price} for product in products]
    redis_client.set('products', json.dumps(products_data))

# Пример запуска Kafka consumer в отдельном потоке
if __name__ == "__main__":
    # Начинаем слушать Kafka сообщения
    while True:
        try:
            consume_from_kafka()
        except Exception as e:
            print(f"Error consuming Kafka message: {e}")
            sleep(5)  # Повторить попытку через 5 секунд
