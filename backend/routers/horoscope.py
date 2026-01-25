from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date, timedelta
from typing import Optional

from database import get_session
from models.zodiac import ZodiacSign, ZodiacSignRead, ZodiacSignWithDetails
from models.horoscope import WeeklyHoroscope, WeeklyHoroscopeRead, WeeklyHoroscopeWithZodiac

router = APIRouter(prefix="/api/horoscope", tags=["Horoscope"])


def get_current_week_start() -> date:
    """取得本週一的日期"""
    today = date.today()
    return today - timedelta(days=today.weekday())


@router.get("/zodiac", response_model=list[ZodiacSignWithDetails])
def get_all_zodiac_signs(session: Session = Depends(get_session)):
    """取得所有星座資料"""
    signs = session.exec(select(ZodiacSign).order_by(ZodiacSign.id)).all()
    return [ZodiacSignWithDetails.from_db(sign) for sign in signs]


@router.get("/zodiac/{code}", response_model=ZodiacSignWithDetails)
def get_zodiac_by_code(code: str, session: Session = Depends(get_session)):
    """取得指定星座資料"""
    sign = session.exec(
        select(ZodiacSign).where(ZodiacSign.code == code.upper())
    ).first()

    if not sign:
        raise HTTPException(status_code=404, detail="星座不存在")

    return ZodiacSignWithDetails.from_db(sign)


@router.get("/weekly/{code}", response_model=WeeklyHoroscopeWithZodiac)
def get_weekly_horoscope(
    code: str,
    week_start: Optional[date] = None,
    session: Session = Depends(get_session)
):
    """取得指定星座的週運勢"""
    if week_start is None:
        week_start = get_current_week_start()

    # 取得星座
    sign = session.exec(
        select(ZodiacSign).where(ZodiacSign.code == code.upper())
    ).first()

    if not sign:
        raise HTTPException(status_code=404, detail="星座不存在")

    # 取得週運勢
    horoscope = session.exec(
        select(WeeklyHoroscope)
        .where(WeeklyHoroscope.zodiac_id == sign.id)
        .where(WeeklyHoroscope.week_start == week_start)
    ).first()

    if not horoscope:
        raise HTTPException(
            status_code=404,
            detail=f"尚無 {sign.name_zh} 本週運勢資料"
        )

    return WeeklyHoroscopeWithZodiac(
        **horoscope.model_dump(),
        zodiac_code=sign.code,
        zodiac_name=sign.name_zh,
        zodiac_symbol=sign.symbol
    )


@router.get("/weekly", response_model=list[WeeklyHoroscopeWithZodiac])
def get_all_weekly_horoscopes(
    week_start: Optional[date] = None,
    session: Session = Depends(get_session)
):
    """取得所有星座的週運勢"""
    if week_start is None:
        week_start = get_current_week_start()

    signs = session.exec(select(ZodiacSign).order_by(ZodiacSign.id)).all()
    sign_map = {s.id: s for s in signs}

    horoscopes = session.exec(
        select(WeeklyHoroscope)
        .where(WeeklyHoroscope.week_start == week_start)
        .order_by(WeeklyHoroscope.zodiac_id)
    ).all()

    result = []
    for h in horoscopes:
        sign = sign_map.get(h.zodiac_id)
        if sign:
            result.append(WeeklyHoroscopeWithZodiac(
                **h.model_dump(),
                zodiac_code=sign.code,
                zodiac_name=sign.name_zh,
                zodiac_symbol=sign.symbol
            ))

    return result
