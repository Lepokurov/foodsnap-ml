from datetime import date, datetime, timezone


def parse_requested_date(value: date | None) -> date:
    return value or datetime.now(timezone.utc).date()

