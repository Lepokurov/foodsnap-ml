from typing import Any

from app.services.food_data_client import USDAFoodDataCentralClient


class FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {
            "foods": [
                {
                    "fdcId": 123,
                    "description": "Bananas, raw",
                    "foodNutrients": [
                        {
                            "nutrientName": "Energy",
                            "nutrientNumber": "208",
                            "unitName": "kcal",
                            "value": 89,
                        }
                    ],
                }
            ]
        }


def test_usda_search_uses_post_json_body(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        *,
        params: dict[str, Any],
        json: dict[str, Any],
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["params"] = params
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("app.services.food_data_client.httpx.post", fake_post)

    candidates = USDAFoodDataCentralClient(
        api_key="test-key",
        base_url="https://example.test/fdc/v1",
        timeout_seconds=3.0,
    ).search_calories(label="banana", limit=3)

    assert captured["url"] == "https://example.test/fdc/v1/foods/search"
    assert captured["params"] == {"api_key": "test-key"}
    assert captured["json"] == {
        "query": "banana",
        "pageSize": 3,
        "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
    }
    assert captured["timeout"] == 3.0
    assert len(candidates) == 1
    assert candidates[0].calories == 89
