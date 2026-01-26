"""Cron Job 路由 - 供 Render Cron Job 呼叫"""
import logging
from datetime import date, timedelta
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlmodel import Session, select

from config import get_settings
from database import get_session
from models.zodiac import ZodiacSign
from models.horoscope import WeeklyHoroscope
from services.claude_ai import claude_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cron", tags=["Cron"])
settings = get_settings()


def verify_cron_secret(x_cron_secret: str = Header(None)):
    """驗證 Cron Job 密鑰"""
    # 必須設定 CRON_SECRET 才能呼叫 cron 端點
    if not settings.cron_secret:
        logger.warning("CRON_SECRET 未設定，拒絕 cron 請求")
        raise HTTPException(status_code=403, detail="Cron secret not configured")
    if x_cron_secret != settings.cron_secret:
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
            element_zh = element_map.get(sign.element, sign.element)
            logger.info(f"開始生成 {sign.name_zh} 週運勢")
            try:
                result = await claude_service.generate_weekly_horoscope(
                    zodiac_name=sign.name_zh,
                    zodiac_element=element_zh,
                    current_aspects=[],
                    retrograde_planets=[]
                )
            except Exception as ai_error:
                logger.exception(f"AI 呼叫異常 ({sign.name_zh}): {ai_error}")
                errors.append(f"{sign.name_zh}: AI 異常 - {str(ai_error)}")
                continue

            if not result:
                logger.warning(f"{sign.name_zh}: AI 回傳 None")
                errors.append(f"{sign.name_zh}: AI 生成失敗 (回傳空)")
                continue

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
            logger.info(f"{sign.name_zh} 週運勢生成完成")

        except Exception as e:
            logger.exception(f"生成 {sign.name_zh} 週運勢時發生錯誤")
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
