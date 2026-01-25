from sqlmodel import SQLModel, Field
from datetime import datetime, date
from typing import Optional


class WeeklyHoroscopeBase(SQLModel):
    """週運勢基本欄位"""
    zodiac_id: int = Field(foreign_key="zodiac_signs.id")
    week_start: date
    summary: str
    love_advice: Optional[str] = None
    career_advice: Optional[str] = None
    health_advice: Optional[str] = None
    lucky_day: Optional[str] = Field(default=None, max_length=10)
    lucky_color: Optional[str] = Field(default=None, max_length=20)
    lucky_number: Optional[int] = None
    overall_score: Optional[int] = Field(default=None, ge=1, le=5)


class WeeklyHoroscope(WeeklyHoroscopeBase, table=True):
    """週運勢資料表"""
    __tablename__ = "weekly_horoscope"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WeeklyHoroscopeRead(WeeklyHoroscopeBase):
    """週運勢回應模型"""
    id: int
    created_at: datetime


class WeeklyHoroscopeWithZodiac(WeeklyHoroscopeRead):
    """週運勢含星座資訊"""
    zodiac_code: str
    zodiac_name: str
    zodiac_symbol: str
