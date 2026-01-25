"""Cron Job 路由 - 供 Render Cron Job 呼叫"""
import os
from fastapi import APIRouter, Header, HTTPException

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
