from pathlib import Path
from typing import Protocol

import boto3

from app.core.config import get_settings
from app.services.image_loader import MealImage


class MealClassifier(Protocol):
    model_version: str

    def classify(self, image: MealImage) -> list[tuple[str, float]]:
        pass


class StubMealClassifier:
    model_version = "stub-v1"

    def classify(self, image: MealImage) -> list[tuple[str, float]]:
        file_name = Path(image.object_name or image.source_uri).name.lower()
        keywords = {
            "burger": ("burger", 0.91),
            "pizza": ("pizza", 0.94),
            "salad": ("salad", 0.88),
            "pasta": ("pasta", 0.87),
            "sushi": ("sushi", 0.9),
            "steak": ("steak", 0.86),
            "soup": ("soup", 0.79),
            "banana": ("banana", 0.9),
        }
        for keyword, result in keywords.items():
            if keyword in file_name:
                return [result]
        return [("mixed_plate", 0.58)]


class RekognitionMealClassifier:
    model_version = "aws-rekognition-labels-v1"

    def classify(self, image: MealImage) -> list[tuple[str, float]]:
        settings = get_settings()
        client = boto3.client("rekognition", region_name=settings.aws_region)
        if image.s3_bucket and image.s3_key:
            rekognition_image = {
                "S3Object": {
                    "Bucket": image.s3_bucket,
                    "Name": image.s3_key,
                }
            }
        elif image.content:
            rekognition_image = {"Bytes": image.content}
        else:
            raise ValueError("Image content or S3 location is required for classification.")

        response = client.detect_labels(
            Image=rekognition_image,
            MaxLabels=10,
            MinConfidence=50,
        )
        candidates = []
        for label in response.get("Labels", []):
            name = str(label.get("Name", "")).strip().lower()
            if not name:
                continue
            confidence = float(label.get("Confidence", 0)) / 100
            candidates.append((name, confidence))

        return candidates or [("mixed_plate", 0.5)]


def create_meal_classifier() -> MealClassifier:
    settings = get_settings()
    if settings.meal_classifier_backend == "stub":
        return StubMealClassifier()
    if settings.meal_classifier_backend == "aws_rekognition":
        return RekognitionMealClassifier()
    raise ValueError(f"Unsupported meal classifier backend: {settings.meal_classifier_backend}")
