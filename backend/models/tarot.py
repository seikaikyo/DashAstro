from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class TarotCardBase(SQLModel):
    """塔羅牌基本欄位"""
    number: int = Field(unique=True, index=True)
    name_zh: str = Field(max_length=50)
    name_en: str = Field(max_length=50)
    keywords: list[str] = Field(default=[], sa_column=Column(JSON))
    upright_meaning: str
    reversed_meaning: str
    image_url: Optional[str] = Field(default=None, max_length=255)


class TarotCard(TarotCardBase, table=True):
    """塔羅牌資料表"""
    __tablename__ = "tarot_cards"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TarotCardRead(TarotCardBase):
    """塔羅牌回應模型"""
    id: int


class TarotSpreadBase(SQLModel):
    """牌陣基本欄位"""
    code: str = Field(max_length=20, unique=True, index=True)
    name_zh: str = Field(max_length=50)
    description: Optional[str] = None
    card_count: int
    positions: list[dict] = Field(default=[], sa_column=Column(JSON))
    suitable_questions: list[str] = Field(default=[], sa_column=Column(JSON))


class TarotSpread(TarotSpreadBase, table=True):
    """牌陣資料表"""
    __tablename__ = "tarot_spreads"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TarotSpreadRead(TarotSpreadBase):
    """牌陣回應模型"""
    id: int


class DrawnCard(SQLModel):
    """抽取的牌"""
    card_id: int
    position: int
    position_name: str
    is_reversed: bool = False


class TarotReadingBase(SQLModel):
    """塔羅解讀基本欄位"""
    spread_id: Optional[int] = None
    question: Optional[str] = None
    cards_drawn: list[DrawnCard] = Field(default=[], sa_column=Column(JSON))
    ai_interpretation: Optional[str] = None
    session_id: Optional[str] = Field(default=None, max_length=100)


class TarotReading(TarotReadingBase, table=True):
    """塔羅解讀資料表"""
    __tablename__ = "tarot_readings"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TarotReadingRead(TarotReadingBase):
    """塔羅解讀回應模型"""
    id: UUID
    created_at: datetime


class CompatibilityContext(SQLModel):
    """配對資訊"""
    user_zodiac: str  # 用戶星座代碼
    user_gender: Optional[str] = None
    partner_zodiac: str  # 對象星座代碼
    partner_gender: Optional[str] = None
    partner_nickname: Optional[str] = None


class DrawRequest(SQLModel):
    """抽牌請求"""
    spread_code: str = "single"
    question: Optional[str] = None
    session_id: Optional[str] = None
    compatibility: Optional[CompatibilityContext] = None


class InterpretRequest(SQLModel):
    """AI 解讀請求"""
    reading_id: UUID
    additional_context: Optional[str] = None
    compatibility: Optional[CompatibilityContext] = None
