import re
from datetime import datetime, timezone
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def build_upload_filename(meal_id: str, original_name: str, suffix: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", original_name).strip("-").lower() or "meal"
    return f"{meal_id}_{stem}_{timestamp}{suffix}"
