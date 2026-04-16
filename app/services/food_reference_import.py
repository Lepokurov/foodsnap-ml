from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.food_reference import FoodReference
from app.services.food_data_client import FoodDataProvider


SUPPORTED_SOURCES = {"usda_fdc"}
SUPPORTED_MODES = {"upsert", "insert_missing"}


class FoodReferenceImportService:
    def __init__(self, session: Session, food_data_provider: FoodDataProvider) -> None:
        self._session = session
        self._food_data_provider = food_data_provider

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

            estimated_calories = self._estimate_calories_from_provider(
                label=label,
                limit=limit_per_label,
            )
            if estimated_calories is None:
                continue

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

    def _estimate_calories_from_provider(
        self,
        *,
        label: str,
        limit: int,
    ) -> int | None:
        candidates = self._food_data_provider.search_calories(label=label, limit=limit)
        if not candidates:
            return None

        total_calories = sum(candidate.calories for candidate in candidates)
        return round(total_calories / len(candidates))

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
