from fastapi import APIRouter, Depends
from sqlmodel import Session, text
from database import get_session
from config import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


@router.get("/health/db")
def db_health_check(session: Session = Depends(get_session)):
    """資料庫健康檢查"""
    try:
        session.exec(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
