from pathlib import Path


class StubMealClassifier:
    model_version = "stub-v1"

    def classify(self, image_url: str) -> tuple[str, float]:
        file_name = Path(image_url).name.lower()
        keywords = {
            "burger": ("burger", 0.91),
            "pizza": ("pizza", 0.94),
            "salad": ("salad", 0.88),
            "pasta": ("pasta", 0.87),
            "sushi": ("sushi", 0.9),
            "steak": ("steak", 0.86),
            "soup": ("soup", 0.79),
        }
        for keyword, result in keywords.items():
            if keyword in file_name:
                return result
        return "mixed_plate", 0.58


stub_meal_classifier = StubMealClassifier()

