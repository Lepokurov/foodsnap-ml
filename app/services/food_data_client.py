from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from app.core.config import get_settings


@dataclass(frozen=True)
class FoodCalorieCandidate:
    external_id: str
    description: str
    calories: int


class FoodDataProvider(Protocol):
    def search_calories(
        self,
        *,
        label: str,
        limit: int,
    ) -> list[FoodCalorieCandidate]:
        pass


class USDAFoodDataCentralClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 15.0,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.usda_fdc_api_key
        self._base_url = (base_url or settings.usda_fdc_base_url).rstrip("/")
        self._timeout_seconds = timeout_seconds

    def search_calories(
        self,
        *,
        label: str,
        limit: int,
    ) -> list[FoodCalorieCandidate]:
        response = httpx.post(
            f"{self._base_url}/foods/search",
            params={
                "api_key": self._api_key,
            },
            json={
                "query": label,
                "pageSize": limit,
                "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
            },
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()

        foods = response.json().get("foods", [])
        if not isinstance(foods, list):
            return []

        candidates: list[FoodCalorieCandidate] = []
        for food in foods[:limit]:
            if not isinstance(food, dict):
                continue
            calories = self._extract_kcal(food)
            if calories is None:
                continue

            external_id = str(food.get("fdcId", ""))
            description = str(food.get("description", label))
            candidates.append(
                FoodCalorieCandidate(
                    external_id=external_id,
                    description=description,
                    calories=calories,
                )
            )

        return candidates

    @staticmethod
    def _extract_kcal(food: dict[str, Any]) -> int | None:
        nutrients = food.get("foodNutrients", [])
        if not isinstance(nutrients, list):
            return None

        for nutrient in nutrients:
            if not isinstance(nutrient, dict):
                continue

            name = str(nutrient.get("nutrientName", "")).lower()
            number = str(nutrient.get("nutrientNumber", ""))
            unit = str(nutrient.get("unitName", "")).upper()
            value = nutrient.get("value")

            is_energy = "energy" in name or number in {"208", "1008"}
            is_kcal = unit in {"KCAL", "KILOCALORIE", "KILOCALORIES"}
            if not is_energy or not is_kcal or value is None:
                continue

            try:
                return round(float(value))
            except (TypeError, ValueError):
                return None

        return None
