import pytest
import httpx
import os

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8080")


class TestAPISimple:

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.client = httpx.Client(
            base_url=BASE_URL,
            timeout=10.0,
            follow_redirects=True
        )

    def test_get_reports(self):
        """Тест получения отчетов."""
        response = self.client.get("/api/reports")
        assert response.status_code == 200
        data = response.json()
        assert "endpoint" in data
        print(f"/api/reports : получено {len(data.get('data', []))} записей")
        print(data)

    def test_get_reports_with_date(self):
        """Тест получения отчетов с датой."""
        response = self.client.get("/api/reports?date=2024-01-15")
        assert response.status_code == 200
        data = response.json()
        assert data.get("date") == "2024-01-15"
        print(f"/api/reports?date=2024-01-15 : работает")
        print(data)
