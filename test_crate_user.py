import requests

# Адрес вашего запущенного сервера
BASE_URL = "http://localhost:8000"

def test_create_user():
    # Данные нового пользователя
    user_data = {
        "username": "tек_user",
        "email": "tоооt@example.com",
        "description": "Тестовый пользователь для проверки API"
    }

    # Отправляем POST-запрос на /users
    response = requests.post(
        f"{BASE_URL}/users",
        json=user_data
    )

    print("Статус-код:", response.status_code)

    if response.status_code == 201 or response.status_code == 200:
        user = response.json()
        print("Пользователь создан успешно!")
        print("Ответ:", user)
        return user
    else:
        print("Ошибка при создании пользователя:", response.json())
        return None

if __name__ == "__main__":
    test_create_user()