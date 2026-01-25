from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class ZodiacSignBase(SQLModel):
    """星座基本欄位"""
    code: str = Field(max_length=3, unique=True, index=True)
    name_zh: str = Field(max_length=10)
    name_en: str = Field(max_length=20)
    symbol: str = Field(max_length=5)
    element: str = Field(max_length=10)  # fire, earth, air, water
    modality: str = Field(max_length=10)  # cardinal, fixed, mutable
    ruling_planet: str = Field(max_length=20)
    date_start: str = Field(max_length=5)  # MM-DD
    date_end: str = Field(max_length=5)  # MM-DD


class ZodiacSign(ZodiacSignBase, table=True):
    """星座資料表"""
    __tablename__ = "zodiac_signs"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ZodiacSignRead(ZodiacSignBase):
    """星座回應模型"""
    id: int


class ZodiacSignWithDetails(ZodiacSignRead):
    """星座詳細資訊 (含計算屬性)"""
    element_zh: str = ""
    modality_zh: str = ""

    @classmethod
    def from_db(cls, sign: ZodiacSign) -> "ZodiacSignWithDetails":
        element_map = {
            "fire": "火象",
            "earth": "土象",
            "air": "風象",
            "water": "水象"
        }
        modality_map = {
            "cardinal": "開創",
            "fixed": "固定",
            "mutable": "變動"
        }
        return cls(
            **sign.model_dump(),
            element_zh=element_map.get(sign.element, sign.element),
            modality_zh=modality_map.get(sign.modality, sign.modality)
        )
