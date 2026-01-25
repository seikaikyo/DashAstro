"""使用統計 API"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional

from database import get_session
from services.stats import stats_service
from models.stats import Features

router = APIRouter(prefix="/api/stats", tags=["Statistics"])


@router.get("/summary")
def get_stats_summary(
    days: int = Query(default=30, ge=1, le=365),
    session: Session = Depends(get_session)
):
    """取得使用統計摘要"""
    return stats_service.get_summary(session, days)


@router.get("/daily")
def get_daily_stats(
    feature: Optional[str] = None,
    days: int = Query(default=7, ge=1, le=90),
    session: Session = Depends(get_session)
):
    """取得每日統計資料"""
    return {
        "data": stats_service.get_daily_stats(session, feature, days)
    }


@router.get("/trend/{feature}")
def get_feature_trend(
    feature: str,
    days: int = Query(default=30, ge=1, le=365),
    session: Session = Depends(get_session)
):
    """取得特定功能趨勢"""
    return {
        "feature": feature,
        "days": days,
        "data": stats_service.get_feature_trend(session, feature, days)
    }


@router.get("/features")
def get_available_features():
    """取得可追蹤的功能列表"""
    return {
        "features": [
            {"code": Features.WEEKLY_HOROSCOPE, "name": "週運勢"},
            {"code": Features.MONTHLY_HOROSCOPE, "name": "月運勢"},
            {"code": Features.TAROT_DRAW, "name": "塔羅抽牌"},
            {"code": Features.TAROT_INTERPRET, "name": "AI 解讀"},
            {"code": Features.COMPATIBILITY, "name": "配對分析"},
            {"code": Features.SKY_VIEW, "name": "今日天象"},
        ]
    }
