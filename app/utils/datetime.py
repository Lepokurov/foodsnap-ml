from datetime import date, datetime, timezone


def same_utc_day(timestamp: datetime, requested_date: date) -> bool:
    return timestamp.astimezone(timezone.utc).date() == requested_date

