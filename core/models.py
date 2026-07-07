from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class PrayerName(str, Enum):
    FAJR = "Fajr"
    DHUHR = "Dhuhr"
    ASR = "Asr"
    MAGHRIB = "Maghrib"
    ISHA = "Isha"


class ValidationStatus(str, Enum):
    VALID = "VALID"
    LATE = "LATE"


class TreeStageName(str, Enum):
    SEED = "Seed"
    SPROUT = "Sprout"
    SAPLING = "Sapling"
    YOUNG_TREE = "Young Tree"
    MATURE_TREE = "Mature Tree"


class UserProfile(BaseModel):
    name: str
    city: str
    country: str = ""


class PrayerTiming(BaseModel):
    prayer_name: PrayerName
    date: str  # ISO date, e.g. "2026-07-06"
    adhan_time: datetime


class ValidationResult(BaseModel):
    prayer_name: PrayerName
    date: str
    status: ValidationStatus
    adhan_time: datetime
    tick_time: datetime
    minutes_after_adhan: float


class PrayerLogEntry(BaseModel):
    prayer_name: PrayerName
    date: str
    status: ValidationStatus
    logged_at: datetime


class TreeState(BaseModel):
    on_time_count: int
    stage: TreeStageName
    stage_emoji: str
    milestone_reached: bool
