# Food Data Sources

This document records candidate external data sources for the food-reference import consumer.

The API service does not call these providers directly. It only publishes a RabbitMQ task. The `consumers/food_reference_import` microservice consumes that task and calls the configured provider.

## Recommended first provider: USDA FoodData Central

Use `usda_fdc` first.

Why:
- it is a government-backed nutrition database
- it exposes search and details endpoints
- it is better suited for calorie and nutrient reference data than generic recipe APIs
- its data is public domain / CC0

Important details:
- API guide: `https://fdc.nal.usda.gov/api-guide.html`
- API key is required through data.gov
- default rate limit is documented as 1,000 requests per hour per IP
- useful endpoints include `/foods/search` and `/food/{fdcId}`

Suggested worker behavior:
- search each requested label with `/foods/search`
- prefer useful data types for generic foods, such as `Foundation`, `SR Legacy`, and `Survey (FNDDS)`
- extract calories from nutrients, typically energy in kcal
- normalize the result into `food_reference.label` and `food_reference.estimated_calories`

Current implementation:
- `USDAFoodDataCentralClient` calls `/foods/search`
- it reads kcal energy from `foodNutrients`
- `FoodReferenceImportService` averages returned kcal candidates for each label
- labels with no external kcal candidates are skipped instead of receiving fake fallback values

## Current food-reference gap

Recognition now returns candidates from AWS Rekognition and resolves them through `food_reference`. This means the most useful next data task is not another classifier path; it is filling `food_reference` with the labels that Rekognition commonly emits.

The initial seed set is deliberately small:

```text
burger, pizza, salad, pasta, sushi, steak, soup, banana, unknown
```

Recommended next labels to import or curate:

```text
apple, orange, sandwich, bread, cake, cookie, donut, fries, rice, noodles,
egg, chicken, fish, meat, cheese, vegetable, fruit, potato, tomato, avocado
```

Use `POST /api/v1/food-reference/imports` with `source=usda_fdc`, `mode=upsert`, and a small `limit_per_label` first. Review imported calorie values before trusting them broadly, because generic labels can map to different serving assumptions.

For labels that USDA resolves poorly or too broadly, manually curated rows in `food_reference` are acceptable for the MVP as long as they stay approximate and transparent.

## Secondary provider candidate: Open Food Facts

Use `open_food_facts` later, mainly for packaged or branded products. It is documented as a future candidate and is not currently accepted by the API contract.

Why:
- very large open food products database
- useful for branded foods, barcodes, ingredients, and nutrition labels

Tradeoffs:
- less ideal for generic dish labels like `pizza`, `salad`, or `soup`
- data is community-contributed and can be incomplete
- search API has stricter documented rate limits than product lookup

Important details:
- API docs: `https://openfoodfacts.github.io/openfoodfacts-server/api/`
- database license is Open Database License
- individual contents use the Database Contents License
- product images use Creative Commons Attribution ShareAlike

## Not ideal for this use case

`TheMealDB` can be useful for recipe-like examples and dish metadata, but it is not a nutrition database. It should not be the first source for calorie estimates.

## Current queue contract

The API publishes import requests to:

```text
foodsnap.food_reference_import
```

Message contract:

```json
{
  "event_type": "food_reference.import.requested",
  "version": 1,
  "import_request_id": "food_import_abc123",
  "source": "usda_fdc",
  "labels": ["pizza", "salad", "burger"],
  "limit_per_label": 3,
  "mode": "upsert",
  "requested_by_user_id": "user_abc123",
  "occurred_at": "2026-04-15T12:00:00+00:00"
}
```
