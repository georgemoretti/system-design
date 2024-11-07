-- Создание базы данных
CREATE DATABASE shopdb;

-- Подключение к базе данных
\c shopdb;

-- Создание таблицы пользователей с полями для хранения хешированного пароля
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс для быстрого поиска по имени пользователя
CREATE INDEX IF NOT EXISTS idx_username ON users(username);

-- Создание таблицы для товаров
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL
);

-- Индекс для быстрого поиска по имени товара
CREATE INDEX IF NOT EXISTS idx_product_name ON products(name);

-- Создание таблицы для корзины
CREATE TABLE IF NOT EXISTS carts (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    quantity INT NOT NULL DEFAULT 1
);

-- Индекс для быстрого поиска по user_id и product_id
CREATE INDEX IF NOT EXISTS idx_cart_user_product ON carts(user_id, product_id);

-- Тестовые данные для пользователей
INSERT INTO users (username, email, hashed_password, age) VALUES 
('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 30),
('alice', 'alice@example.com', '$2b$12$KIX/1Q0B1gYH3C8.x0ZQ1Oe1fS0f8s7H9r9a5e6q2gG1H5Xv4e5kO', 25),
('bob', 'bob@example.com', '$2b$12$D9U1Zc4F3lW4uD9gF3lW6uOe7f5s8s7H9r9a5e6q2gG1H5Xv4e5kO', 30),
('charlie', 'charlie@example.com', '$2b$12$A3L2F0Q0B1gYH3C8.x0ZQ1Oe1fS0f8s7H9r9a5e6q2gG1H5Xv4e5kO', 22)
ON CONFLICT DO NOTHING;

-- Тестовые данные для товаров
INSERT INTO products (name, price) VALUES
('Laptop', 1200.00),
('Smartphone', 800.00),
('Tablet', 500.00),
('Headphones', 200.00)
ON CONFLICT DO NOTHING;

-- Тестовые данные для корзины
INSERT INTO carts (user_id, product_id, quantity) VALUES
(2, 1, 1),
(2, 3, 2),
(3, 2, 1),
(4, 4, 3)
ON CONFLICT DO NOTHING;