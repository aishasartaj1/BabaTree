from datetime import datetime, timedelta

from core.models import PrayerName, ValidationResult, ValidationStatus


def validate_prayer_time(
    prayer_name: PrayerName,
    date: str,
    adhan_time: datetime,
    tick_time: datetime,
    window_minutes: int = 20,
) -> ValidationResult:
    """Determine whether a prayer was logged on-time (within window_minutes of adhan_time).

    A prayer is VALID only if adhan_time <= tick_time <= adhan_time + window_minutes.
    Ticking before the Adhan has occurred is also treated as LATE (it isn't on-time).
    """
    window_end = adhan_time + timedelta(minutes=window_minutes)
    minutes_after = (tick_time - adhan_time).total_seconds() / 60

    is_valid = adhan_time <= tick_time <= window_end
    status = ValidationStatus.VALID if is_valid else ValidationStatus.LATE

    return ValidationResult(
        prayer_name=prayer_name,
        date=date,
        status=status,
        adhan_time=adhan_time,
        tick_time=tick_time,
        minutes_after_adhan=round(minutes_after, 2),
    )
