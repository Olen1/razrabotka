# Лабораторная работа 3: CRUD с Litestar и SQLAlchemy ORM

Это веб-приложение на Python, реализующее CRUD (Create, Read, Update, Delete) для сущности "Пользователь" с использованием:

- **Фреймворк**: [Litestar](https://litestar.dev/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) (асинхронный)
- **База данных**: SQLite (через `aiosqlite`)
- **Валидация данных**: [Pydantic v2](https://docs.pydantic.dev/)
- **Сервер**: [Uvicorn](https://www.uvicorn.org/)

## Структура проекта

razrabotka/
├── app/
│ ├── init.py
│ ├── main.py
│ ├── controllers/
│ │ ├── init.py
│ │ └── user_controller.py
│ ├── services/
│ │ ├── init.py
│ │ └── user_service.py
│ ├── repositories/
│ │ ├── init.py
│ │ └── user_repository.py
│ ├── models/
│ │ ├── init.py
│ │ ├── Base.py
│ │ └── User.py
│ └── User_schem.py
├── README.md
└── ...


## Установка и запуск

### 1. Клонирование репозитория (если применимо)

Если вы клонируете репозиторий:

```bash
git clone <your-repo-url>
cd razrabotka

2. Установка Python и виртуального окружения
Убедитесь, что у вас установлен Python 3.8 или выше.

Создайте виртуальное окружение:

python -m venv .venv

Активируйте его:

Windows (CMD): .venv\Scripts\activate.bat

3. Установка зависимостей
Убедитесь, что виртуальное окружение активировано, и выполните:
pip install litestar sqlalchemy aiosqlite uvicorn pydantic[email]

4. Запуск приложения
Из корня проекта (razrabotka/) выполните:
python -m app.main

Вы должны увидеть сообщение: INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

Приложение будет доступно по адресу http://localhost:8000.

5. Тестирование API
Вы можете использовать curl, Postman или написать Python-скрипт для тестирования.

Примеры запросов
Создать пользователя (POST /users)

curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "email": "test@example.com", "description": "Тестовый пользователь"}'

Получить всех пользователей (GET /users)
curl http://localhost:8000/users

Получить пользователя по ID (GET /users/{id})
curl http://localhost:8000/users/ВАШ_UUID

Обновить пользователя (PUT /users/{id}
curl -X PUT http://localhost:8000/users/ВАШ_UUID \
  -H "Content-Type: application/json" \
  -d '{"username": "updated_user", "email": "updated@example.com"}'

Удалить пользователя (DELETE /users/{id}
curl -X DELETE http://localhost:8000/users/ВАШ_UUID

