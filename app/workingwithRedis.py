import redis

# Создаем подключение к Redis
client = redis.Redis(
    host='localhost',  # или 'redis' если в Docker сети
    port=6379,
    db=0,
    decode_responses=True  # чтобы получать строки вместо bytes
)

try:
    # 1. Строковые значения
    client.set("user:name", "Иван")
    name = client.get("user:name")  # decode не нужен из-за decode_responses=True

    client.setex("session:123", 3600, "active")  # 1 час

    client.set("counter", 0)
    client.incr("counter")        # Увеличить на 1
    client.incrby("counter", 5)   # Увеличить на 5
    client.decr("counter")

    # 2. Списки
    # Добавление элементов
    client.lpush("tasks", "task1", "task2")  # В начало
    client.rpush("tasks", "task3", "task4")  # В конец

    # Получение элементов
    tasks = client.lrange("tasks", 0, -1)   # Все элементы
    first_task = client.lpop("tasks")       # Удалить и вернуть первый
    last_task = client.rpop("tasks")        # Удалить и вернуть последний

    # Получение длины списка
    length = client.llen("tasks")

    # 3. Множества
    # Добавление элементов
    client.sadd("tags", "python", "redis", "database")
    client.sadd("languages", "python", "java", "javascript")

    # Проверка принадлежности
    is_member = client.sismember("tags", "python")  # True

    # Получение всех элементов
    all_tags = client.smembers("tags")

    # Операции с множествами
    intersection = client.sinter("tags", "languages")  # Пересечение
    union = client.sunion("tags", "languages")         # Объединение
    difference = client.sdiff("tags", "languages")     # Разность

    # 4. Хэши
    # Установка полей
    client.hset("user:1000", mapping={
        "name": "Иван",
        "age": "30",
        "city": "Москва"
    })

    # Получение значений
    name = client.hget("user:1000", "name")
    all_data = client.hgetall("user:1000")

    # Проверка существования поля
    exists = client.hexists("user:1000", "email")

    # Получение всех ключей или значений
    keys = client.hkeys("user:1000")
    values = client.hvals("user:1000")

    # 5. Упорядоченные множества
    # Добавление элементов с оценкой
    client.zadd("leaderboard", {
        "player1": 100,
        "player2": 200,
        "player3": 150
    })

    # Получение элементов по рангу (топ-3)
    top_players = client.zrange("leaderboard", 0, 2, withscores=True)

    # Получение элементов по оценке (между 100 и 200)
    players_by_score = client.zrangebyscore("leaderboard", 100, 200, withscores=True)

    # Получение ранга элемента
    rank = client.zrank("leaderboard", "player1")

    print("Все операции выполнены успешно!")

except redis.RedisError as e:
    print(f"Ошибка Redis: {e}")
except Exception as e:
    print(f"Общая ошибка: {e}")
finally:
    # Закрываем соединение
    client.close()