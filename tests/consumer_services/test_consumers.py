from datetime import datetime, timezone

from app.db.models.food_reference import FoodReference
from app.db.models.user import User
from app.db.repositories.meals import MealRepository
from app.db.session import get_db_session
from consumers.food_reference_import.main import process_message as process_food_import
from consumers.meal_analysis.main import process_message as process_meal_analysis


def test_meal_analysis_consumer_processes_valid_message() -> None:
    meal_id = "meal_consumer_test"
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
            image_url="data/uploads/pizza-test.jpg",
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


def test_food_reference_import_consumer_upserts_labels() -> None:
    process_food_import(
        {
            "event_type": "food_reference.import.requested",
            "version": 1,
            "import_request_id": "food_import_consumer_test",
            "source": "usda_fdc",
            "labels": ["Pizza", "ramen", "ramen"],
            "limit_per_label": 2,
            "mode": "upsert",
        }
    )

    with get_db_session() as session:
        pizza = session.get(FoodReference, "pizza")
        ramen = session.get(FoodReference, "ramen")
        assert pizza is not None
        assert pizza.estimated_calories == 700
        assert ramen is not None
        assert ramen.estimated_calories == 450
