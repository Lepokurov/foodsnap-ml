from datetime import datetime, timezone

from app.ml.classifier import stub_meal_classifier
from app.ml.label_mapping import normalize_label
from app.services.calorie_estimator import calorie_estimator_service
from app.services.state import PredictionRecord, store


class MealAnalysisService:
    def process_meal(self, meal_id: str) -> None:
        meal = store.meals.get(meal_id)
        if meal is None:
            return

        meal.status = "processing"
        meal.updated_at = datetime.now(timezone.utc)

        raw_label, confidence = stub_meal_classifier.classify(meal.image_url)
        normalized_label = normalize_label(raw_label)
        estimated_calories = calorie_estimator_service.estimate(normalized_label)

        meal.status = "done"
        meal.recognized_label = normalized_label
        meal.confidence = confidence
        meal.estimated_calories = estimated_calories
        meal.updated_at = datetime.now(timezone.utc)

        store.predictions[meal_id] = PredictionRecord(
            meal_id=meal_id,
            raw_label=raw_label,
            normalized_label=normalized_label,
            confidence=confidence,
            model_version=stub_meal_classifier.model_version,
        )


meal_analysis_service = MealAnalysisService()

