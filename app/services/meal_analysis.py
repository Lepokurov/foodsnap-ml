from app.db.repositories.meals import MealRepository
from app.ml.classifier import MealClassifier
from app.services.calorie_estimator import CalorieEstimatorService
from app.services.image_loader import MealImageLoader


class MealAnalysisService:
    def __init__(
        self,
        meals: MealRepository,
        calorie_estimator: CalorieEstimatorService,
        image_loader: MealImageLoader,
        classifier: MealClassifier,
    ) -> None:
        self._meals = meals
        self._calorie_estimator = calorie_estimator
        self._image_loader = image_loader
        self._classifier = classifier

    def process_meal(self, meal_id: str) -> None:
        meal = self._meals.mark_processing(meal_id)
        if meal is None:
            return

        image = self._image_loader.load(meal)
        candidates = self._classifier.classify(image)
        raw_label = candidates[0][0] if candidates else "unknown"
        normalized_label, confidence = self._calorie_estimator.resolve_label(candidates)
        estimated_calories = self._calorie_estimator.estimate(normalized_label)

        self._meals.complete(
            meal_id=meal_id,
            raw_label=raw_label,
            recognized_label=normalized_label,
            confidence=confidence,
            estimated_calories=estimated_calories,
            model_version=self._classifier.model_version,
        )
