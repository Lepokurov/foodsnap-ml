from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.food_reference import FoodReference
from app.db.session import DEFAULT_FOOD_REFERENCE
SUPPORTED_SOURCES = {"usda_fdc", "open_food_facts"}
SUPPORTED_MODES = {"upsert", "insert_missing"}


class FoodReferenceImportService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def import_labels(
        self,
        *,
        source: str,
        labels: list[str],
        limit_per_label: int,
        mode: str,
    ) -> int:
        if source not in SUPPORTED_SOURCES:
            raise ValueError(f"Unsupported food-reference source: {source}")
        if mode not in SUPPORTED_MODES:
            raise ValueError(f"Unsupported food-reference import mode: {mode}")
        if limit_per_label < 1:
            raise ValueError("limit_per_label must be greater than zero")

        imported_count = 0
        for label in self._normalize_unique(labels):
            existing = self._session.get(FoodReference, label)
            if existing is not None and mode == "insert_missing":
                continue

            estimated_calories = self._estimate_calories(label, existing)
            if existing is None:
                self._session.add(
                    FoodReference(
                        label=label,
                        estimated_calories=estimated_calories,
                    )
                )
            else:
                existing.estimated_calories = estimated_calories
                existing.updated_at = datetime.now(timezone.utc)

            imported_count += 1

        self._session.flush()
        return imported_count

    def _estimate_calories(
        self,
        label: str,
        existing: FoodReference | None,
    ) -> int:
        if label in DEFAULT_FOOD_REFERENCE:
            return DEFAULT_FOOD_REFERENCE[label]
        if existing is not None:
            return existing.estimated_calories
        return DEFAULT_FOOD_REFERENCE["unknown"]

    def _normalize_unique(self, labels: list[str]) -> list[str]:
        normalized_labels: list[str] = []
        seen: set[str] = set()
        for label in labels:
            normalized_label = label.strip().lower()
            if not normalized_label or normalized_label in seen:
                continue
            normalized_labels.append(normalized_label)
            seen.add(normalized_label)
        return normalized_labels
