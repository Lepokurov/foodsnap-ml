import time

from fastapi.testclient import TestClient

from app.main import create_app


def test_healthcheck() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"


def test_auth_upload_and_summary_flow() -> None:
    with TestClient(create_app()) as client:
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "supersecret",
                "full_name": "Food Tester",
            },
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]

        upload_response = client.post(
            "/api/v1/meals",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("pizza-lunch.jpg", b"fake-image-bytes", "image/jpeg")},
        )
        assert upload_response.status_code == 201
        meal_id = upload_response.json()["id"]

        time.sleep(0.15)

        meal_response = client.get(
            f"/api/v1/meals/{meal_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert meal_response.status_code == 200
        assert meal_response.json()["status"] == "done"
        assert meal_response.json()["recognized_label"] == "pizza"

        summary_response = client.get(
            "/api/v1/summary/daily",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert summary_response.status_code == 200
        assert summary_response.json()["processed_meals"] == 1
        assert summary_response.json()["total_estimated_calories"] == 700
