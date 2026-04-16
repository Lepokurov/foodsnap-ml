from typing import Literal

from pydantic import BaseModel, Field, field_validator


FoodReferenceImportSource = Literal["usda_fdc"]
FoodReferenceImportMode = Literal["upsert", "insert_missing"]


class FoodReferenceImportRequest(BaseModel):
    source: FoodReferenceImportSource = "usda_fdc"
    labels: list[str] = Field(
        default_factory=lambda: [
            "burger",
            "pizza",
            "salad",
            "pasta",
            "sushi",
            "steak",
            "soup",
        ],
        min_length=1,
        max_length=100,
    )
    limit_per_label: int = Field(default=3, ge=1, le=25)
    mode: FoodReferenceImportMode = "upsert"

    @field_validator("labels")
    @classmethod
    def normalize_labels(cls, labels: list[str]) -> list[str]:
        normalized = [label.strip().lower() for label in labels if label.strip()]
        if not normalized:
            raise ValueError("At least one non-empty label is required.")
        return list(dict.fromkeys(normalized))


class FoodReferenceImportResponse(BaseModel):
    queued: bool
    event_type: str
    import_request_id: str
    queue: str
    source: str
    labels: list[str]
    limit_per_label: int
    mode: str
