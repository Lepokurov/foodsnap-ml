from app.db.repositories.meals import MealRepository
from app.ml.classifier import stub_meal_classifier
from app.ml.label_mapping import normalize_label
from app.services.calorie_estimator import calorie_estimator_service


class MealAnalysisService:
    def __init__(self) -> None:
        self._meals = MealRepository()

    def process_meal(self, meal_id: str) -> None:
        meal = self._meals.mark_processing(meal_id)
        if meal is None:
            return

        raw_label, confidence = stub_meal_classifier.classify(meal.image_url)
        normalized_label = normalize_label(raw_label)
        estimated_calories = calorie_estimator_service.estimate(normalized_label)

        self._meals.complete(
            meal_id=meal_id,
            raw_label=raw_label,
            recognized_label=normalized_label,
            confidence=confidence,
            estimated_calories=estimated_calories,
            model_version=stub_meal_classifier.model_version,
        )


meal_analysis_service = MealAnalysisService()
