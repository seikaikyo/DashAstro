from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Optional
from sqlmodel import Session

from database import get_session
from services.ephemeris import ephemeris_service
from services.astrology import astrology_service
from models.stats import Features
from services.stats import stats_service

router = APIRouter(prefix="/api/astronomy", tags=["Astronomy"])


@router.get("/planets")
async def get_planet_positions(datetime_str: Optional[str] = None):
    """
    取得行星位置

    datetime_str: ISO 格式時間字串，預設為當前時間
    """
    try:
        dt = datetime.fromisoformat(datetime_str) if datetime_str else None
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的時間格式")

    positions = ephemeris_service.get_planet_positions(dt)

    return {
        "datetime": (dt or datetime.utcnow()).isoformat(),
        "planets": positions
    }


@router.get("/retrograde")
async def get_retrograde_planets(datetime_str: Optional[str] = None):
    """取得目前逆行的行星"""
    try:
        dt = datetime.fromisoformat(datetime_str) if datetime_str else None
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的時間格式")

    retrograde = ephemeris_service.get_retrograde_planets(dt)

    return {
        "datetime": (dt or datetime.utcnow()).isoformat(),
        "retrograde_planets": retrograde,
        "count": len(retrograde)
    }


@router.get("/moon-phase")
async def get_moon_phase(datetime_str: Optional[str] = None):
    """取得月相"""
    try:
        dt = datetime.fromisoformat(datetime_str) if datetime_str else None
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的時間格式")

    phase = ephemeris_service.get_moon_phase(dt)

    return {
        "datetime": (dt or datetime.utcnow()).isoformat(),
        **phase
    }


@router.get("/aspects")
async def get_aspects(datetime_str: Optional[str] = None):
    """取得當前行星相位"""
    try:
        dt = datetime.fromisoformat(datetime_str) if datetime_str else None
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的時間格式")

    aspects = astrology_service.get_all_aspects(dt)

    return {
        "datetime": (dt or datetime.utcnow()).isoformat(),
        "aspects": aspects,
        "count": len(aspects)
    }


@router.get("/summary")
async def get_sky_summary(
    datetime_str: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """取得當前天象摘要"""
    try:
        dt = datetime.fromisoformat(datetime_str) if datetime_str else None
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的時間格式")

    summary = astrology_service.get_current_sky_summary(dt)

    # 記錄使用統計
    stats_service.log_usage(session, Features.SKY_VIEW)

    return summary
