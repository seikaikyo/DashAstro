from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import get_settings
from database import init_db
from routers import health_router, horoscope_router, tarot_router, astronomy_router, compatibility_router, stats_router

settings = get_settings()


def update_tarot_meanings():
    """更新塔羅牌義為白話版本"""
    from sqlmodel import Session, select
    from database import engine
    from models.tarot import TarotCard

    MEANINGS = {
        0: ("準備好開始新的事情了！放輕鬆，跟著感覺走就對了。", "想太少就衝了，可能會踩到坑。先停下來想清楚再行動。"),
        1: ("你手上資源夠，能力也有，該做就做吧！", "有能力但沒好好用，可能在拖延或自我懷疑。"),
        2: ("相信你的第六感，它通常是對的。有些事不用急著說出來。", "直覺被忽略了，可能想太多。有些事情還沒浮出水面。"),
        3: ("好事要發生了！適合開始新計畫、經營感情、或做有創意的事。", "靈感枯竭或太依賴別人。記得也要照顧自己。"),
        4: ("該拿出主導權了。設定目標、建立規矩，讓事情有條有理地進行。", "控制慾太強或管太多。放鬆一點，不是所有事都要照你的方式。"),
        5: ("可以找有經驗的人請教，或照傳統方式來處理。", "別太墨守成規，試試新方法。不是所有建議都適合你。"),
        6: ("感情順利，或是面臨重要選擇。選你真心想要的。", "價值觀衝突或選擇困難。先搞清楚什麼對你最重要。"),
        7: ("衝就對了！你有能力克服障礙，堅持下去會成功的。", "方向不對或太急躁。暫停一下，確認目標再出發。"),
        8: ("用耐心和溫柔來處理困難，你比你想的更強。", "自信不足或太壓抑情緒。承認自己的感受沒關係。"),
        9: ("給自己一些獨處的時間，好好想想接下來要怎麼走。", "太封閉自己了，該出來透透氣。別一個人扛所有事。"),
        10: ("運勢要轉變了，可能是好的改變。順著變化走，抓住機會。", "暫時卡住了，但這只是過渡期。耐心等待，轉機會來的。"),
        11: ("公平處理事情，做該做的決定。誠實面對自己和別人。", "有些事不太公平，或是在逃避責任。面對現實比較好。"),
        12: ("換個角度看事情會有新發現。暫時的犧牲可能換來更大的收穫。", "白白犧牲了卻沒結果。該放手的就放手，別再拖了。"),
        13: ("一個階段要結束了，但這是新開始的前兆。放下舊的，迎接新的。", "抗拒改變只會更痛苦。接受事實，讓自己往前走。"),
        14: ("保持平衡，凡事適可而止。急不得的事就慢慢來。", "失去平衡了，可能做過頭或太極端。調整一下步調。"),
        15: ("有什麼在困住你？可能是壞習慣或不健康的關係。意識到問題是解決的第一步。", "準備掙脫束縛了！但要小心，別又陷入另一個陷阱。"),
        16: ("意外的變動，打亂了原本的計畫。雖然混亂，但這是重新開始的機會。", "在逃避必要的改變，但拖越久越痛苦。不如早點面對。"),
        17: ("希望來了！經歷困難後，前方有光明。保持信心，好事正在路上。", "有點失去信心，但別放棄。這只是暫時的低潮。"),
        18: ("事情不是表面看起來那樣，小心被誤導。相信直覺，但也要看清現實。", "迷霧散開了，真相慢慢浮現。或者，別再自欺欺人了。"),
        19: ("超讚！一切都很順利，充滿正能量。享受這段好時光吧！", "好事會來，只是慢了一點。別太悲觀，陽光就在雲後面。"),
        20: ("是時候做個了結了。回顧過去，做出重要決定，然後向前看。", "還沒準備好面對現實？總是要面對的，拖越久越難處理。"),
        21: ("恭喜！完成了一個階段，可以慶祝一下。準備好迎接下一個挑戰了嗎？", "差一點點就完成了，別半途而廢。或是害怕結束、不想面對結果。"),
    }

    with Session(engine) as session:
        # 檢查是否需要更新 (用愚者牌檢查)
        card = session.exec(select(TarotCard).where(TarotCard.number == 0)).first()
        if card and "準備好開始新的事情" in card.upright_meaning:
            print("[啟動] 牌義已是白話版本，跳過更新")
            return

        for number, (upright, reversed) in MEANINGS.items():
            card = session.exec(select(TarotCard).where(TarotCard.number == number)).first()
            if card:
                card.upright_meaning = upright
                card.reversed_meaning = reversed
                session.add(card)
        session.commit()
        print("[啟動] 已更新塔羅牌義為白話版本")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時
    if settings.database_url:
        init_db()
        try:
            update_tarot_meanings()
        except Exception as e:
            print(f"[啟動] 更新牌義失敗: {e}")
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
app.include_router(compatibility_router)
app.include_router(stats_router)


@app.get("/")
async def root():
    """根端點"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs"
    }
