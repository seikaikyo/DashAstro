"""宿曜道 API 路由"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from database import get_session
from services.sukuyodo import sukuyodo_service
from services.stats import stats_service
from models.stats import Features

router = APIRouter(prefix="/api/sukuyodo", tags=["宿曜道"])


class CompatibilityRequest(BaseModel):
    """相性診斷請求"""
    date1: str  # YYYY-MM-DD
    date2: str  # YYYY-MM-DD


@router.get("/mansions")
async def get_all_mansions():
    """
    取得 27 宿列表

    返回所有本命宿的基本資料，包含名稱、讀音、元素等。
    """
    mansions = sukuyodo_service.get_all_mansions()

    # 只回傳基本資料，不包含詳細描述
    return {
        "count": len(mansions),
        "mansions": [
            {
                "index": m["index"],
                "name_jp": m["name_jp"],
                "reading": m["reading"],
                "element": m["element"],
                "keywords": m["keywords"]
            }
            for m in mansions
        ]
    }


@router.get("/mansion/{date_str}")
def get_mansion_by_date(
    date_str: str,
    session: Session = Depends(get_session)
):
    """
    根據西曆生日查詢本命宿

    Args:
        date_str: 西曆生日，格式 YYYY-MM-DD

    Returns:
        本命宿完整資料，包含性格分析、感情運、事業運等
    """
    try:
        birth_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="日期格式錯誤，請使用 YYYY-MM-DD"
        )

    # 驗證日期範圍
    today = date.today()
    if birth_date > today:
        raise HTTPException(
            status_code=400,
            detail="生日不可為未來日期"
        )

    if birth_date.year < 1900:
        raise HTTPException(
            status_code=400,
            detail="僅支援 1900 年後的日期"
        )

    mansion = sukuyodo_service.get_mansion(birth_date)

    # 記錄使用統計
    stats_service.log_usage(session, Features.SUKUYODO_LOOKUP)

    return {
        "success": True,
        "data": mansion
    }


@router.post("/compatibility")
def calculate_compatibility(
    request: CompatibilityRequest,
    session: Session = Depends(get_session)
):
    """
    計算雙人相性

    根據兩人的西曆生日計算宿曜道相性，
    返回關係類型、相性分數及建議。
    """
    try:
        date1 = date.fromisoformat(request.date1)
        date2 = date.fromisoformat(request.date2)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="日期格式錯誤，請使用 YYYY-MM-DD"
        )

    # 驗證日期
    today = date.today()
    for d in [date1, date2]:
        if d > today:
            raise HTTPException(
                status_code=400,
                detail="生日不可為未來日期"
            )
        if d.year < 1900:
            raise HTTPException(
                status_code=400,
                detail="僅支援 1900 年後的日期"
            )

    result = sukuyodo_service.calculate_compatibility(date1, date2)

    # 記錄使用統計
    stats_service.log_usage(session, Features.SUKUYODO_COMPATIBILITY)

    return {
        "success": True,
        "data": result
    }


@router.get("/relations")
async def get_relation_types():
    """
    取得六種關係類型說明

    返回命、業胎、榮親、友衰、安壞、危成六種關係的詳細說明。
    """
    relations = sukuyodo_service.relations_data

    return {
        "count": len(relations),
        "relations": [
            {
                "type": key,
                "name": rel["name"],
                "name_jp": rel.get("name_jp", rel["name"]),
                "score": rel["score"],
                "description": rel["description"],
                "advice": rel["advice"]
            }
            for key, rel in relations.items()
        ]
    }
