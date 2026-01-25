"""使用統計模型"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from datetime import date as date_type
from typing import Optional


class UsageStatsBase(SQLModel):
    """使用統計基本欄位"""
    feature: str = Field(index=True, max_length=50)  # 功能名稱
    stat_date: date_type = Field(index=True)  # 統計日期
    count: int = Field(default=0)  # 使用次數


class UsageStats(UsageStatsBase, table=True):
    """使用統計資料表"""
    __tablename__ = "usage_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UsageStatsRead(UsageStatsBase):
    """使用統計回應模型"""
    id: int
    created_at: datetime
    updated_at: datetime


# 功能名稱常數
class Features:
    """功能名稱定義"""
    WEEKLY_HOROSCOPE = "weekly_horoscope"      # 週運勢查看
    MONTHLY_HOROSCOPE = "monthly_horoscope"    # 月運勢查看
    TAROT_DRAW = "tarot_draw"                  # 塔羅抽牌
    TAROT_INTERPRET = "tarot_interpret"        # AI 解讀
    COMPATIBILITY = "compatibility"            # 配對分析
    SKY_VIEW = "sky_view"                      # 今日天象
