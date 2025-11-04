import requests


BASE_URL = "http://localhost:8000"

def test_get_all_users():

    response = requests.get(f"{BASE_URL}/users")

    print("Статус-код:", response.status_code)

    if response.status_code == 200:
        users = response.json()
        print(f"Найдено пользователей: {len(users)}")
        for user in users:
            print(f"- ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
    else:
        print("Ошибка при получении пользователей:", response.json())

def test_get_users_with_pagination():

    response = requests.get(f"{BASE_URL}/users?count=5&page=1")

    print("\nСтатус-код ):", response.status_code)

    if response.status_code == 200:
        users = response.json()
        print(f"Найдено пользователей (count=5): {len(users)}")
        for user in users:
            print(f"- ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
    else:
        print("Ошибка при получении пользователей:", response.json())

if __name__ == "__main__":
    test_get_all_users()
    test_get_users_with_pagination()