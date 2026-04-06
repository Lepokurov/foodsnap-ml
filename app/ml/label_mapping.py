LABEL_MAPPING = {
    "mixed_plate": "unknown",
    "burger": "burger",
    "pizza": "pizza",
    "salad": "salad",
    "pasta": "pasta",
    "sushi": "sushi",
    "steak": "steak",
    "soup": "soup",
}


def normalize_label(raw_label: str) -> str:
    return LABEL_MAPPING.get(raw_label, "unknown")

