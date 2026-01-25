"""吉日 API 路由"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Query
from services.japanese_calendar import japanese_calendar

router = APIRouter(prefix="/api/lucky-days", tags=["吉日"])


@router.get("/today")
async def get_today_lucky_info():
    """查詢今日吉凶資訊"""
    today = date.today()
    stem, branch, _ = japanese_calendar.get_day_ganzhi(today)
    rokuyo = japanese_calendar.get_rokuyo(today)
    is_ichiryu = japanese_calendar.is_ichiryu_manbai(today)

    types = []
    if is_ichiryu:
        types.append("一粒萬倍日")
    if rokuyo == "大安":
        types.append("大安")

    return {
        "date": today.isoformat(),
        "weekday": ["日", "一", "二", "三", "四", "五", "六"][today.weekday()],
        "ganzhi": f"{stem}{branch}",
        "rokuyo": rokuyo,
        "is_ichiryu_manbai": is_ichiryu,
        "is_taian": rokuyo == "大安",
        "lucky_types": types,
        "is_double_lucky": is_ichiryu and rokuyo == "大安",
        "description": _get_day_description(is_ichiryu, rokuyo)
    }


@router.get("/month/{year}/{month}")
async def get_month_lucky_days(
    year: int,
    month: int,
    day_type: str = Query("all", description="吉日類型: all, ichiryu_manbai, taian")
):
    """查詢指定月份的吉日"""
    if month < 1 or month > 12:
        return {"error": "月份須為 1-12"}

    lucky_days = japanese_calendar.get_month_lucky_days(year, month, day_type)

    return {
        "year": year,
        "month": month,
        "day_type": day_type,
        "count": len(lucky_days),
        "days": lucky_days
    }


@router.get("/next")
async def get_next_lucky_day(
    day_type: str = Query("ichiryu_manbai", description="吉日類型: ichiryu_manbai, taian, all")
):
    """查詢下一個吉日"""
    next_day = japanese_calendar.get_next_lucky_day(day_type=day_type)

    if next_day:
        return {
            "found": True,
            **next_day
        }
    else:
        return {
            "found": False,
            "message": "60 天內無符合條件的吉日"
        }


@router.get("/range")
async def get_lucky_days_in_range(
    start: str = Query(..., description="開始日期 YYYY-MM-DD"),
    end: str = Query(..., description="結束日期 YYYY-MM-DD"),
    day_type: str = Query("all", description="吉日類型: all, ichiryu_manbai, taian")
):
    """查詢指定範圍的吉日"""
    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError:
        return {"error": "日期格式錯誤，請使用 YYYY-MM-DD"}

    if end_date < start_date:
        return {"error": "結束日期不可早於開始日期"}

    if (end_date - start_date).days > 365:
        return {"error": "查詢範圍不可超過一年"}

    lucky_days = japanese_calendar.get_lucky_days_in_range(
        start_date, end_date, day_type
    )

    return {
        "start": start,
        "end": end,
        "day_type": day_type,
        "count": len(lucky_days),
        "days": lucky_days
    }


@router.get("/check/{date_str}")
async def check_date(date_str: str):
    """檢查指定日期的吉凶"""
    try:
        check_date = date.fromisoformat(date_str)
    except ValueError:
        return {"error": "日期格式錯誤，請使用 YYYY-MM-DD"}

    stem, branch, _ = japanese_calendar.get_day_ganzhi(check_date)
    rokuyo = japanese_calendar.get_rokuyo(check_date)
    is_ichiryu = japanese_calendar.is_ichiryu_manbai(check_date)

    types = []
    if is_ichiryu:
        types.append("一粒萬倍日")
    if rokuyo == "大安":
        types.append("大安")

    return {
        "date": check_date.isoformat(),
        "weekday": ["日", "一", "二", "三", "四", "五", "六"][check_date.weekday()],
        "ganzhi": f"{stem}{branch}",
        "rokuyo": rokuyo,
        "is_ichiryu_manbai": is_ichiryu,
        "is_taian": rokuyo == "大安",
        "lucky_types": types,
        "is_double_lucky": is_ichiryu and rokuyo == "大安",
        "description": _get_day_description(is_ichiryu, rokuyo)
    }


def _get_day_description(is_ichiryu: bool, rokuyo: str) -> str:
    """產生吉日說明"""
    parts = []

    if is_ichiryu and rokuyo == "大安":
        return "雙重吉日！一粒萬倍日遇上大安，特別適合開展新事業、簽約、求職等重大決定。"

    if is_ichiryu:
        parts.append("一粒萬倍日：開始新事物會有萬倍回報的吉日，適合創業、投資、開店、播種等")

    rokuyo_desc = {
        "大安": "大安：六曜中最吉利的日子，諸事皆宜",
        "友引": "友引：適合喜事，但應避免喪事",
        "先勝": "先勝：上午吉、下午凶，急事宜早辦",
        "先負": "先負：上午凶、下午吉，宜靜待時機",
        "赤口": "赤口：只有正午前後為吉，其餘時段不宜",
        "佛滅": "佛滅：諸事不宜的日子，適合休養生息"
    }

    if rokuyo in rokuyo_desc:
        parts.append(rokuyo_desc[rokuyo])

    return "；".join(parts) if parts else "普通日"
