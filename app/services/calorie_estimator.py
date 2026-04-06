from app.services.state import store


class CalorieEstimatorService:
    def estimate(self, normalized_label: str) -> int:
        return store.food_reference.get(normalized_label, store.food_reference["unknown"])


calorie_estimator_service = CalorieEstimatorService()

