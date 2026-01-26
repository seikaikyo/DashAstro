from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
import random

from config import get_settings
from database import get_session
from models.tarot import (
    TarotCard, TarotCardRead,
    TarotSpread, TarotSpreadRead,
    TarotReading, TarotReadingRead,
    DrawRequest, DrawnCard, InterpretRequest,
    CompatibilityContext
)
from models.stats import Features
from services.stats import stats_service

settings = get_settings()
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

    # 記錄使用統計
    stats_service.log_usage(session, Features.TAROT_DRAW)

    return reading


@router.get("/readings/{reading_id}", response_model=TarotReadingRead)
def get_reading(reading_id: str, session: Session = Depends(get_session)):
    """取得解讀紀錄"""
    reading = session.get(TarotReading, reading_id)

    if not reading:
        raise HTTPException(status_code=404, detail="解讀紀錄不存在")

    return reading


@router.get("/ai-status")
def get_ai_status():
    """檢查 AI 服務狀態"""
    from services.claude_ai import claude_service
    return claude_service.get_status()


@router.get("/ai-test")
def test_ai_service():
    """測試 AI 服務"""
    from services.claude_ai import claude_service
    from anthropic import Anthropic

    status = claude_service.get_status()
    result = {"status": status, "test_result": None, "error": None}

    if not status.get("available"):
        result["error"] = "服務不可用"
        return result

    try:
        response = claude_service.client.messages.create(
            model=settings.claude_model,
            max_tokens=50,
            messages=[{"role": "user", "content": "說 OK"}]
        )
        result["test_result"] = response.content[0].text
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"

    return result


@router.post("/interpret")
async def interpret_reading(
    request: InterpretRequest,
    session: Session = Depends(get_session)
):
    """AI 解讀塔羅牌"""
    from services.claude_ai import claude_service

    reading = session.get(TarotReading, request.reading_id)

    if not reading:
        raise HTTPException(status_code=404, detail="解讀紀錄不存在")

    # 如果已有解讀，直接回傳
    if reading.ai_interpretation:
        return {
            "reading_id": str(reading.id),
            "interpretation": reading.ai_interpretation,
            "cached": True
        }

    # 取得牌陣名稱
    spread = session.get(TarotSpread, reading.spread_id)
    spread_name = spread.name_zh if spread else "單牌"

    # 取得每張牌的詳細資料
    cards_for_ai = []
    for drawn in reading.cards_drawn:
        card = session.exec(
            select(TarotCard).where(TarotCard.id == drawn.get("card_id"))
        ).first()
        if card:
            is_reversed = drawn.get("is_reversed", False)
            cards_for_ai.append({
                "name_zh": card.name_zh,
                "position_name": drawn.get("position_name", ""),
                "is_reversed": is_reversed,
                "keywords": card.keywords,
                "meaning": card.reversed_meaning if is_reversed else card.upright_meaning
            })

    # 準備配對資訊
    compatibility_data = None
    if request.compatibility:
        compatibility_data = {
            "user_zodiac": request.compatibility.user_zodiac,
            "user_gender": request.compatibility.user_gender,
            "partner_zodiac": request.compatibility.partner_zodiac,
            "partner_gender": request.compatibility.partner_gender,
            "partner_nickname": request.compatibility.partner_nickname
        }

    # 呼叫 Claude AI 解讀
    interpretation = await claude_service.interpret_tarot_reading(
        cards=cards_for_ai,
        question=reading.question,
        spread_name=spread_name,
        compatibility=compatibility_data
    )

    if interpretation:
        # 儲存解讀結果
        reading.ai_interpretation = interpretation
        session.add(reading)
        session.commit()

        # 記錄使用統計
        stats_service.log_usage(session, Features.TAROT_INTERPRET)

        return {
            "reading_id": str(reading.id),
            "interpretation": interpretation,
            "cached": False
        }

    return {
        "reading_id": str(reading.id),
        "interpretation": None,
        "message": "AI 服務暫時無法使用"
    }
