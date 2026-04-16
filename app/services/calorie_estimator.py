from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.food_reference import FoodReference


class CalorieEstimatorService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def resolve_label(self, candidates: list[tuple[str, float]]) -> tuple[str, float]:
        normalized_candidates = [
            (raw_label.strip().lower(), confidence)
            for raw_label, confidence in candidates
            if raw_label.strip()
        ]
        candidate_labels = [label for label, _ in normalized_candidates]
        if not candidate_labels:
            return "unknown", 0.0

        references = set(
            self._session.scalars(
                select(FoodReference.label).where(
                    FoodReference.label.in_(candidate_labels),
                    FoodReference.label != "unknown",
                )
            )
        )

        for normalized_label, confidence in normalized_candidates:
            if normalized_label in references:
                return normalized_label, confidence

        _, fallback_confidence = normalized_candidates[0]
        return "unknown", fallback_confidence

    def estimate(self, normalized_label: str) -> int:
        reference = self._session.scalar(
            select(FoodReference).where(FoodReference.label == normalized_label)
        )
        if reference is not None:
            return reference.estimated_calories

        fallback = self._session.get(FoodReference, "unknown")
        return fallback.estimated_calories if fallback is not None else 450
