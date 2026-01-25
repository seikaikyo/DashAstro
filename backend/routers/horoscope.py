from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date, timedelta, datetime
from typing import Optional

from database import get_session
from models.zodiac import ZodiacSign, ZodiacSignRead, ZodiacSignWithDetails
from models.horoscope import (
    WeeklyHoroscope, WeeklyHoroscopeRead, WeeklyHoroscopeWithZodiac,
    MonthlyHoroscope, MonthlyHoroscopeRead, MonthlyHoroscopeWithZodiac
)

router = APIRouter(prefix="/api/horoscope", tags=["Horoscope"])

MONTH_NAMES = {
    1: "一月", 2: "二月", 3: "三月", 4: "四月",
    5: "五月", 6: "六月", 7: "七月", 8: "八月",
    9: "九月", 10: "十月", 11: "十一月", 12: "十二月"
}


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


# === 月運勢 ===

@router.get("/monthly/{code}")
async def get_monthly_horoscope(
    code: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """取得指定星座的月運勢"""
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # 取得星座
    sign = session.exec(
        select(ZodiacSign).where(ZodiacSign.code == code.upper())
    ).first()

    if not sign:
        raise HTTPException(status_code=404, detail="星座不存在")

    # 取得月運勢
    horoscope = session.exec(
        select(MonthlyHoroscope)
        .where(MonthlyHoroscope.zodiac_id == sign.id)
        .where(MonthlyHoroscope.year == year)
        .where(MonthlyHoroscope.month == month)
    ).first()

    # 如果沒有資料，嘗試用 AI 生成
    if not horoscope:
        horoscope = await generate_monthly_horoscope(sign, year, month, session)

    if not horoscope:
        raise HTTPException(
            status_code=404,
            detail=f"尚無 {sign.name_zh} {month}月運勢資料"
        )

    return {
        **horoscope.model_dump(),
        "zodiac_code": sign.code,
        "zodiac_name": sign.name_zh,
        "zodiac_symbol": sign.symbol,
        "month_name": MONTH_NAMES.get(month, f"{month}月")
    }


async def generate_monthly_horoscope(
    sign: ZodiacSign,
    year: int,
    month: int,
    session: Session
) -> Optional[MonthlyHoroscope]:
    """用 AI 生成月運勢"""
    from services.claude_ai import claude_service

    if not claude_service._is_available():
        return None

    # 元素對應
    element_map = {
        "fire": "火象", "earth": "土象", "air": "風象", "water": "水象"
    }
    element_zh = element_map.get(sign.element, "")

    prompt = f"""你是朋友圈裡最會看星座的那個人，說話直接但溫暖。

幫 {sign.name_zh}（{element_zh}）寫 {year}年{month}月的運勢，用 JSON 格式回覆：
{{
  "summary": "整體運勢，約 100 字，講這個月的重點",
  "love_advice": "感情運，約 60 字",
  "career_advice": "工作運，約 60 字",
  "health_advice": "健康提醒，約 40 字",
  "lucky_days": "幸運日期，如 3, 15, 22",
  "lucky_color": "幸運色",
  "lucky_number": 數字(1-99),
  "overall_score": 整體評分(1-5)
}}

語氣要求：
- 台灣口語，像在跟朋友聊天
- 直接說重點，不要繞圈子
- 具體可執行的建議
- 只回 JSON，不要其他文字"""

    try:
        response = claude_service.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        result_text = response.content[0].text.strip()
        # 移除可能的 markdown
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1]
        if result_text.endswith("```"):
            result_text = result_text.rsplit("\n", 1)[0]

        data = json.loads(result_text)

        # 建立並儲存
        horoscope = MonthlyHoroscope(
            zodiac_id=sign.id,
            year=year,
            month=month,
            summary=data.get("summary", ""),
            love_advice=data.get("love_advice"),
            career_advice=data.get("career_advice"),
            health_advice=data.get("health_advice"),
            lucky_days=data.get("lucky_days"),
            lucky_color=data.get("lucky_color"),
            lucky_number=data.get("lucky_number"),
            overall_score=data.get("overall_score")
        )
        session.add(horoscope)
        session.commit()
        session.refresh(horoscope)

        return horoscope
    except Exception as e:
        print(f"生成月運勢失敗: {e}")
        return None
