from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func, select

from app.db.models.food_reference import FoodReference
from app.db.models.user import User
from app.db.repositories.meals import MealRepository
from app.db.session import get_db_session
from app.services.food_data_client import FoodCalorieCandidate
from app.services.food_reference_import import FoodReferenceImportService
from consumers.food_reference_import.main import process_message as process_food_import
from consumers.meal_analysis.main import process_message as process_meal_analysis


def test_meal_analysis_consumer_processes_valid_message() -> None:
    meal_id = "meal_consumer_test"
    image_path = Path("data/uploads/pizza-test.jpg")
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(b"fake-pizza-image")

    with get_db_session() as session:
        session.add(
            User(
                id="user_consumer_test",
                email="consumer@example.com",
                full_name="Consumer Test",
                password_hash="hash",
            )
        )
        MealRepository(session).create(
            id=meal_id,
            user_id="user_consumer_test",
            status="pending",
            image_url=str(image_path),
            image_storage="local",
            meal_timestamp=datetime.now(timezone.utc),
        )

    process_meal_analysis(
        {
            "event_type": "meal.analysis.requested",
            "version": 1,
            "meal_id": meal_id,
        }
    )

    with get_db_session() as session:
        meal = MealRepository(session).get_by_id(meal_id)
        assert meal is not None
        assert meal.status == "done"
        assert meal.recognized_label == "pizza"
        assert meal.estimated_calories == 700


class FakeFoodDataProvider:
    def search_calories(
        self,
        *,
        label: str,
        limit: int,
    ) -> list[FoodCalorieCandidate]:
        calories_by_label = {
            "pizza": 705,
            "ramen": 440,
            "banana": 112,
        }
        calories = calories_by_label.get(label)
        if calories is None:
            return []
        return [
            FoodCalorieCandidate(
                external_id=f"fake-{label}",
                description=label,
                calories=calories,
            )
        ]


def test_food_reference_import_service_upserts_external_labels() -> None:
    with get_db_session() as session:
        imported_count = FoodReferenceImportService(
            session,
            FakeFoodDataProvider(),
        ).import_labels(
            source="usda_fdc",
            labels=["Pizza", "ramen", "unknown-from-provider"],
            limit_per_label=2,
            mode="upsert",
        )

    with get_db_session() as session:
        pizza = session.get(FoodReference, "pizza")
        ramen = session.get(FoodReference, "ramen")
        unknown = session.get(FoodReference, "unknown-from-provider")
        assert imported_count == 2
        assert pizza is not None
        assert pizza.estimated_calories == 705
        assert ramen is not None
        assert ramen.estimated_calories == 440
        assert unknown is None


def test_food_reference_import_service_updates_existing_label() -> None:
    with get_db_session() as session:
        existing_banana = session.get(FoodReference, "banana")
        assert existing_banana is not None
        assert existing_banana.estimated_calories == 105

        imported_count = FoodReferenceImportService(
            session,
            FakeFoodDataProvider(),
        ).import_labels(
            source="usda_fdc",
            labels=["Banana"],
            limit_per_label=2,
            mode="upsert",
        )

    with get_db_session() as session:
        banana = session.get(FoodReference, "banana")
        banana_rows = session.scalar(
            select(func.count(FoodReference.label)).where(FoodReference.label == "banana")
        )
        assert imported_count == 1
        assert banana is not None
        assert banana.estimated_calories == 112
        assert banana_rows == 1


def test_food_reference_import_consumer_ignores_unsupported_source() -> None:
    process_food_import(
        {
            "event_type": "food_reference.import.requested",
            "version": 1,
            "import_request_id": "food_import_consumer_test",
            "source": "open_food_facts",
            "labels": ["ramen"],
            "limit_per_label": 2,
            "mode": "upsert",
        }
    )

    with get_db_session() as session:
        assert session.get(FoodReference, "ramen") is None
