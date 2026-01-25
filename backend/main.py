from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import get_settings
from database import init_db
from routers import health_router, horoscope_router, tarot_router, astronomy_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時
    if settings.database_url:
        init_db()
    yield
    # 關閉時 (如有需要)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="星語塔羅 - 務實科學的占星分析 + AI 智慧解牌",
    lifespan=lifespan
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(health_router)
app.include_router(horoscope_router)
app.include_router(tarot_router)
app.include_router(astronomy_router)


@app.get("/")
async def root():
    """根端點"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs"
    }
