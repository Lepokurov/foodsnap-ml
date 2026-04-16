from app.db.repositories.meals import MealRepository
from app.ml.classifier import MealClassifier
from app.ml.label_mapping import normalize_label
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
        raw_label, confidence = self._classifier.classify(image)
        normalized_label = normalize_label(raw_label)
        estimated_calories = self._calorie_estimator.estimate(normalized_label)

        self._meals.complete(
            meal_id=meal_id,
            raw_label=raw_label,
            recognized_label=normalized_label,
            confidence=confidence,
            estimated_calories=estimated_calories,
            model_version=self._classifier.model_version,
        )
