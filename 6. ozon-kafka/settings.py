import os

# Kafka settings
KAFKA_BOOTSTRAP_SERVERS = "kafka1:9092"
KAFKA_TOPIC = "ozon_routes"

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB settings
MONGO_URI = "mongodb://root:pass@mongo:27017/shopdb"

# Redis settings
REDIS_URL = os.getenv("REDIS_URL", "redis://cache:6379/0")

# PostgreSQL settings
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:archdb@db/ozon"