import requests

BASE_URL = "http://localhost:8000"

def list_all_users():
    try:
        response = requests.get(f"{BASE_URL}/users")
        response.raise_for_status()  # вызовет исключение при 4xx/5xx статусе
        data = response.json()

        print(f"Всего пользователей в системе: {data['total_count']}\n")
        for user in data['users']:
            print(f"ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Description: {user.get('description', '—')}")
            print(f"Created: {user['created_at']}")
            print("-" * 40)

    except requests.exceptions.ConnectionError:
        print("Не удалось подключиться к серверу. Убедитесь, что он запущен на http://localhost:8000")
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e} — сервер вернул статус {response.status_code}")
        print("Ответ:", response.text)
    except KeyError as e:
        print(f"Некорректный формат ответа: отсутствует поле {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    list_all_users()