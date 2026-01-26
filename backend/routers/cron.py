"""Cron Job 路由 - 供 Render Cron Job 呼叫"""
import os
from datetime import date, timedelta
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlmodel import Session, select

from database import get_session
from models.zodiac import ZodiacSign
from models.horoscope import WeeklyHoroscope
from services.claude_ai import claude_service

router = APIRouter(prefix="/api/cron", tags=["Cron"])

# Cron Job 密鑰（防止外部隨意呼叫）
CRON_SECRET = os.getenv("CRON_SECRET", "")


def verify_cron_secret(x_cron_secret: str = Header(None)):
    """驗證 Cron Job 密鑰"""
    if not CRON_SECRET:
        # 未設定密鑰時，允許呼叫（開發環境）
        return True
    if x_cron_secret != CRON_SECRET:
        raise HTTPException(status_code=401, detail="Invalid cron secret")
    return True


@router.post("/milestone-check")
async def milestone_check(x_cron_secret: str = Header(None)):
    """
    每日里程碑檢查

    由 Render Cron Job 每天呼叫一次
    檢查宿曜道使用量是否達到觸發門檻
    """
    verify_cron_secret(x_cron_secret)

    from services.milestone_monitor import milestone_monitor

    results = milestone_monitor.run_daily_check()

    return {
        "success": True,
        "data": results
    }


@router.get("/health")
async def cron_health():
    """Cron 服務健康檢查"""
    return {"status": "ok", "service": "cron"}


def get_current_week_start() -> date:
    """取得本週一日期"""
    today = date.today()
    return today - timedelta(days=today.weekday())


@router.post("/generate-weekly-horoscope")
async def generate_weekly_horoscope(
    x_cron_secret: str = Header(None),
    session: Session = Depends(get_session)
):
    """
    生成本週運勢

    由 Render Cron Job 每週一呼叫
    為 12 個星座生成週運勢並存入資料庫
    """
    verify_cron_secret(x_cron_secret)

    week_start = get_current_week_start()

    # 檢查是否已有本週資料
    existing = session.exec(
        select(WeeklyHoroscope).where(WeeklyHoroscope.week_start == week_start)
    ).first()

    if existing:
        return {
            "success": True,
            "data": {
                "message": "本週運勢已存在",
                "week_start": week_start.isoformat(),
                "generated": 0
            }
        }

    # 取得所有星座
    signs = session.exec(select(ZodiacSign)).all()

    if not signs:
        raise HTTPException(status_code=500, detail="星座資料不存在")

    # 元素對照
    element_map = {
        "fire": "火象",
        "earth": "土象",
        "air": "風象",
        "water": "水象"
    }

    generated_count = 0
    errors = []

    for sign in signs:
        try:
            # 呼叫 AI 生成運勢
            element_zh = element_map.get(sign.element, sign.element)
            result = await claude_service.generate_weekly_horoscope(
                zodiac_name=sign.name_zh,
                zodiac_element=element_zh,
                current_aspects=[],  # 可擴充：傳入當前天象
                retrograde_planets=[]  # 可擴充：傳入逆行行星
            )

            if not result:
                errors.append(f"{sign.name_zh}: AI 生成失敗")
                continue

            # 存入資料庫
            horoscope = WeeklyHoroscope(
                zodiac_id=sign.id,
                week_start=week_start,
                summary=result.get("summary", ""),
                love_advice=result.get("love_advice"),
                career_advice=result.get("career_advice"),
                health_advice=result.get("health_advice"),
                lucky_day=result.get("lucky_day"),
                lucky_color=result.get("lucky_color"),
                lucky_number=result.get("lucky_number"),
                overall_score=result.get("overall_score")
            )
            session.add(horoscope)
            generated_count += 1
            print(f"[Cron] {sign.name_zh} 週運勢生成完成")

        except Exception as e:
            errors.append(f"{sign.name_zh}: {str(e)}")

    session.commit()

    return {
        "success": len(errors) == 0,
        "data": {
            "week_start": week_start.isoformat(),
            "generated": generated_count,
            "total": len(signs),
            "errors": errors if errors else None
        }
    }
