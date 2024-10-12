workspace {
    name "Ozon E-commerce Application"
    description "Архитектура приложения Ozon для управления пользователями, товарами и корзинами"

    !identifiers hierarchical

    model {
        user = person "Пользователь" {
        }

        ozonSystem = softwareSystem "Ozon System" {
            description "Система управления пользователями, товарами и корзинами"

            userDb = container "User Database" {
                technology "PostgreSQL"
                description "База данных для хранения пользователей"
            }

            productDb = container "Product Database" {
                technology "PostgreSQL"
                description "База данных для хранения товаров"
            }

            cartDb = container "Cart Database" {
                technology "PostgreSQL"
                description "База данных для хранения корзин"
            }

            webApp = container "Web Application" {
                technology "React, JavaScript"
                description "Веб-приложение для взаимодействия с пользователями"
            }

            apiGateway = container "API Gateway" {
                technology "Spring Cloud Gateway"
                description "API-шлюз для маршрутизации запросов"
            }

            userService = container "User Service" {
                technology "Java Spring Boot"
                description "Сервис управления пользователями"
                -> apiGateway "Запросы на управление пользователями" "HTTPS"
                -> userDb "Хранение информации о пользователях" "JDBC"
            }

            productService = container "Product Service" {
                technology "Java Spring Boot"
                description "Сервис управления товарами"
                -> apiGateway "Запросы на управление товарами" "HTTPS"
                -> productDb "Хранение информации о товарах" "JDBC"
            }

            cartService = container "Cart Service" {
                technology "Java Spring Boot"
                description "Сервис управления корзинами"
                -> apiGateway "Запросы на управление корзинами" "HTTPS"
                -> cartDb "Хранение информации о корзинах" "JDBC"
            }
        }

        user -> ozonSystem.webApp "Взаимодействует через веб-приложение"

        ozonSystem.webApp -> ozonSystem.apiGateway "Передача запросов" "HTTPS"
    }

    views {
        systemContext ozonSystem {
            include *
            autolayout lr
        }

        container ozonSystem {
            include *
            autolayout lr
        }

        dynamic ozonSystem "addToCart" "Добавление товара в корзину" {
            user -> ozonSystem.webApp "Открывает страницу товара"
            ozonSystem.webApp -> ozonSystem.apiGateway "POST /cart/add"
            ozonSystem.apiGateway -> ozonSystem.cartService "Добавляет товар в корзину"
            ozonSystem.cartService -> ozonSystem.cartDb "INSERT INTO cart"
            autolayout lr
        }

        dynamic ozonSystem "createUser" "Создание нового пользователя" {
            user -> ozonSystem.webApp "Создание нового пользователя"
            ozonSystem.webApp -> ozonSystem.apiGateway "POST /user"
            ozonSystem.apiGateway -> ozonSystem.userService "Создает запись в базе данных"
            ozonSystem.userService -> ozonSystem.userDb "INSERT INTO users"
            autolayout lr
        }

        dynamic ozonSystem "findUserByLogin" "Поиск пользователя по логину" {
            user -> ozonSystem.webApp "Поиск пользователя по логину"
            ozonSystem.webApp -> ozonSystem.apiGateway "GET /user?login={login}"
            ozonSystem.apiGateway -> ozonSystem.userService "Получает пользователя по логину"
            ozonSystem.userService -> ozonSystem.userDb "SELECT * FROM users WHERE login={login}"
            autolayout lr
        }

        dynamic ozonSystem "findUserByName" "Поиск пользователя по маске имени и фамилии" {
            user -> ozonSystem.webApp "Поиск пользователя по имени и фамилии"
            ozonSystem.webApp -> ozonSystem.apiGateway "GET /user?name={name}&surname={surname}"
            ozonSystem.apiGateway -> ozonSystem.userService "Получает пользователя по имени и фамилии"
            ozonSystem.userService -> ozonSystem.userDb "SELECT * FROM users WHERE name LIKE {name} AND surname LIKE {surname}"
            autolayout lr
        }

        dynamic ozonSystem "createProduct" "Создание нового товара" {
            user -> ozonSystem.webApp "Создание нового товара"
            ozonSystem.webApp -> ozonSystem.apiGateway "POST /product"
            ozonSystem.apiGateway -> ozonSystem.productService "Создает запись о товаре"
            ozonSystem.productService -> ozonSystem.productDb "INSERT INTO products"
            autolayout lr
        }

        dynamic ozonSystem "getProducts" "Получение списка товаров" {
            user -> ozonSystem.webApp "Запрашивает список товаров"
            ozonSystem.webApp -> ozonSystem.apiGateway "GET /products"
            ozonSystem.apiGateway -> ozonSystem.productService "Возвращает список товаров"
            ozonSystem.productService -> ozonSystem.productDb "SELECT * FROM products"
            autolayout lr
        }

        dynamic ozonSystem "getCart" "Получение корзины для пользователя" {
            user -> ozonSystem.webApp "Запрашивает корзину"
            ozonSystem.webApp -> ozonSystem.apiGateway "GET /cart"
            ozonSystem.apiGateway -> ozonSystem.cartService "Возвращает корзину"
            ozonSystem.cartService -> ozonSystem.cartDb "SELECT * FROM cart WHERE user_id={user_id}"
            autolayout lr
        }

        theme default
    }
}