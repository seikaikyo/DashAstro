from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from services.compatibility import compatibility_service

router = APIRouter(prefix="/api/compatibility", tags=["Compatibility"])


class CompatibilityRequest(BaseModel):
    """配對請求"""
    sign1: str  # 自己的星座代碼
    sign2: str  # 對方的星座代碼


class WeeklyCompatibilityRequest(BaseModel):
    """週配對請求"""
    sign1: str
    sign2: str


@router.get("/signs")
def get_sign_list():
    """取得星座列表"""
    return [
        {"code": code, "name": name}
        for code, name in compatibility_service.SIGN_NAMES.items()
    ]


@router.post("/analyze")
def analyze_compatibility(request: CompatibilityRequest):
    """分析兩個星座的配對"""
    result = compatibility_service.calculate_compatibility(
        request.sign1,
        request.sign2
    )
    return result


@router.post("/weekly")
def get_weekly_compatibility(request: WeeklyCompatibilityRequest):
    """取得本週配對運勢"""
    result = compatibility_service.get_weekly_compatibility(
        request.sign1,
        request.sign2
    )
    return result


@router.get("/element/{sign_code}")
def get_sign_element(sign_code: str):
    """取得星座元素"""
    element = compatibility_service.get_element(sign_code)
    element_zh = {
        "fire": "火象",
        "earth": "土象",
        "air": "風象",
        "water": "水象"
    }
    return {
        "sign_code": sign_code.upper(),
        "element": element,
        "element_zh": element_zh.get(element, "未知")
    }
