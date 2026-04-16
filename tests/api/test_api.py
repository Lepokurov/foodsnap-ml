import time

from fastapi.testclient import TestClient

from app.db.repositories.meals import MealRepository
from app.db.session import get_db_session
from app.ml.classifier import create_meal_classifier
from app.main import create_app
from app.services.calorie_estimator import CalorieEstimatorService
from app.services.image_loader import MealImageLoader
from app.services.meal_analysis import MealAnalysisService


def test_healthcheck() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"
    assert response.json()["queue"] == "in_memory"


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

        meal_response = client.get(
            f"/api/v1/meals/{meal_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert meal_response.status_code == 200
        assert meal_response.json()["status"] == "pending"
        assert meal_response.json()["recognized_label"] is None

        with get_db_session() as session:
            meal_analysis = MealAnalysisService(
                MealRepository(session),
                CalorieEstimatorService(session),
                MealImageLoader(),
                create_meal_classifier(),
            )
            meal_analysis.process_meal(meal_id)
        time.sleep(0.05)

        processed_meal_response = client.get(
            f"/api/v1/meals/{meal_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert processed_meal_response.status_code == 200
        assert processed_meal_response.json()["status"] == "done"
        assert processed_meal_response.json()["recognized_label"] == "pizza"

        meal_response = processed_meal_response
        assert meal_response.json()["status"] == "done"
        assert meal_response.json()["recognized_label"] == "pizza"

        summary_response = client.get(
            "/api/v1/summary/daily",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert summary_response.status_code == 200
        assert summary_response.json()["processed_meals"] == 1
        assert summary_response.json()["total_estimated_calories"] == 700


def test_food_reference_import_request() -> None:
    with TestClient(create_app()) as client:
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "food-importer@example.com",
                "password": "supersecret",
                "full_name": "Food Importer",
            },
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]

        response = client.post(
            "/api/v1/food-reference/imports",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "source": "usda_fdc",
                "labels": ["Pizza", "salad", "pizza"],
                "limit_per_label": 2,
                "mode": "upsert",
            },
        )

    assert response.status_code == 202
    payload = response.json()
    assert payload["queued"] is True
    assert payload["event_type"] == "food_reference.import.requested"
    assert payload["source"] == "usda_fdc"
    assert payload["labels"] == ["pizza", "salad"]
    assert payload["limit_per_label"] == 2
