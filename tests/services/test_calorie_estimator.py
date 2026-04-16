from app.db.models.food_reference import FoodReference
from app.db.session import get_db_session
from app.services.calorie_estimator import CalorieEstimatorService


def test_resolve_label_uses_food_reference_candidates() -> None:
    with get_db_session() as session:
        normalized_label, confidence = CalorieEstimatorService(session).resolve_label(
            [
                ("food", 0.99),
                ("banana", 0.93),
            ]
        )

    assert normalized_label == "banana"
    assert confidence == 0.93


def test_default_food_reference_includes_banana() -> None:
    with get_db_session() as session:
        banana = session.get(FoodReference, "banana")

    assert banana is not None
    assert banana.estimated_calories == 105
