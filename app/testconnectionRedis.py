import redis
from redis import client

# Подключение к локальному Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Проверка подключения
try:
    r.ping()
    print("Успешное подключение к Redis")
except redis.ConnectionError:
    print("Ошибка подключения к Redis")





