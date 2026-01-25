from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
import random

from database import get_session
from models.tarot import (
    TarotCard, TarotCardRead,
    TarotSpread, TarotSpreadRead,
    TarotReading, TarotReadingRead,
    DrawRequest, DrawnCard, InterpretRequest
)

router = APIRouter(prefix="/api/tarot", tags=["Tarot"])


@router.get("/cards/major", response_model=list[TarotCardRead])
def get_major_arcana(session: Session = Depends(get_session)):
    """取得 22 張大阿爾克那"""
    cards = session.exec(
        select(TarotCard).order_by(TarotCard.number)
    ).all()
    return cards


@router.get("/cards/{number}", response_model=TarotCardRead)
def get_card_by_number(number: int, session: Session = Depends(get_session)):
    """取得指定編號的塔羅牌"""
    card = session.exec(
        select(TarotCard).where(TarotCard.number == number)
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="牌不存在")

    return card


@router.get("/spreads", response_model=list[TarotSpreadRead])
def get_all_spreads(session: Session = Depends(get_session)):
    """取得所有牌陣"""
    spreads = session.exec(
        select(TarotSpread).order_by(TarotSpread.card_count)
    ).all()
    return spreads


@router.get("/spreads/{code}", response_model=TarotSpreadRead)
def get_spread_by_code(code: str, session: Session = Depends(get_session)):
    """取得指定牌陣"""
    spread = session.exec(
        select(TarotSpread).where(TarotSpread.code == code)
    ).first()

    if not spread:
        raise HTTPException(status_code=404, detail="牌陣不存在")

    return spread


@router.post("/draw", response_model=TarotReadingRead)
def draw_cards(
    request: DrawRequest,
    session: Session = Depends(get_session)
):
    """抽牌"""
    # 取得牌陣
    spread = session.exec(
        select(TarotSpread).where(TarotSpread.code == request.spread_code)
    ).first()

    if not spread:
        raise HTTPException(status_code=404, detail="牌陣不存在")

    # 取得所有牌
    all_cards = session.exec(select(TarotCard)).all()
    if len(all_cards) < spread.card_count:
        raise HTTPException(status_code=500, detail="牌庫資料不足")

    # 隨機抽取
    selected_cards = random.sample(all_cards, spread.card_count)

    # 建立抽牌結果
    drawn_cards = []
    for i, (card, pos) in enumerate(zip(selected_cards, spread.positions)):
        is_reversed = random.random() < 0.3  # 30% 機率逆位
        drawn_cards.append(DrawnCard(
            card_id=card.id,
            position=pos.get("position", i + 1),
            position_name=pos.get("name", f"位置 {i + 1}"),
            is_reversed=is_reversed
        ))

    # 儲存解讀紀錄
    reading = TarotReading(
        spread_id=spread.id,
        question=request.question,
        cards_drawn=[dc.model_dump() for dc in drawn_cards],
        session_id=request.session_id
    )
    session.add(reading)
    session.commit()
    session.refresh(reading)

    return reading


@router.get("/readings/{reading_id}", response_model=TarotReadingRead)
def get_reading(reading_id: str, session: Session = Depends(get_session)):
    """取得解讀紀錄"""
    reading = session.get(TarotReading, reading_id)

    if not reading:
        raise HTTPException(status_code=404, detail="解讀紀錄不存在")

    return reading


@router.post("/interpret")
async def interpret_reading(
    request: InterpretRequest,
    session: Session = Depends(get_session)
):
    """AI 解讀塔羅牌 (需要另外實作 Claude 服務)"""
    reading = session.get(TarotReading, request.reading_id)

    if not reading:
        raise HTTPException(status_code=404, detail="解讀紀錄不存在")

    if reading.ai_interpretation:
        return {
            "reading_id": str(reading.id),
            "interpretation": reading.ai_interpretation,
            "cached": True
        }

    # TODO: 整合 Claude AI 服務
    return {
        "reading_id": str(reading.id),
        "interpretation": None,
        "message": "AI 解讀服務開發中"
    }
