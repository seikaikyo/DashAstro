---
title: DashAstro 專案初始化
type: feature
status: in-progress
created: 2026-01-25
---

# DashAstro 專案初始化

## 專案概述

占星結合塔羅的內容網站，基於真實天文資料提供星座運勢分析，搭配 AI 智慧解牌。

**定位**：務實科學的占星分析平台
**域名**：astro.dashai.dev
**風格**：親切日常風

## 核心功能

### Phase 1：基礎架構
- [ ] 專案建置（Vite + Vue 3 + Shoelace）
- [ ] 後端 API（FastAPI + SQLModel + Neon）
- [ ] 基本頁面架構

### Phase 2：星象資料
- [ ] 整合星曆 API（Swiss Ephemeris / Skyfield）
- [ ] 行星位置計算
- [ ] 相位分析
- [ ] 每週星象摘要生成

### Phase 3：塔羅系統
- [ ] 22 張大牌資料庫
- [ ] 牌陣系統（單牌、三牌、凱爾特十字等）
- [ ] 抽牌互動介面

### Phase 4：AI 智慧分析
- [ ] Claude API 整合
- [ ] 每週星座運勢自動生成
- [ ] 塔羅牌個人化解讀
- [ ] 問答追問功能

## 技術架構

```
┌─────────────────────────────────────────────────────┐
│                    前端 (Vercel)                     │
│            Vite + Vue 3 + Shoelace                  │
│              astro.dashai.dev                       │
└─────────────────────┬───────────────────────────────┘
                      │ HTTPS
┌─────────────────────▼───────────────────────────────┐
│                   後端 (Render)                      │
│           FastAPI + SQLModel + Skyfield             │
│              api.astro.dashai.dev                   │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐
   │  Neon   │  │ Claude   │  │ Skyfield │
   │ 資料庫  │  │   API    │  │ 星曆資料 │
   └─────────┘  └──────────┘  └──────────┘
```

## 資料來源

### 星曆資料（免費）
| 來源 | 用途 | 授權 |
|------|------|------|
| Skyfield (Python) | 行星位置計算 | MIT |
| DE440 星曆表 | NASA JPL 精確資料 | Public Domain |
| Swiss Ephemeris | 占星專用計算 | AGPL / 商業授權 |

### 塔羅牌圖片
| 來源 | 授權 |
|------|------|
| Rider-Waite (1909) | Public Domain |
| 或自製插圖 | 原創 |

## 資料庫設計

```sql
-- 星座基本資料
CREATE TABLE zodiac_signs (
    id SERIAL PRIMARY KEY,
    name_zh VARCHAR(10),      -- 牡羊座
    name_en VARCHAR(20),      -- Aries
    element VARCHAR(10),      -- 火象
    modality VARCHAR(10),     -- 開創
    ruling_planet VARCHAR(20) -- 火星
);

-- 塔羅牌
CREATE TABLE tarot_cards (
    id SERIAL PRIMARY KEY,
    number INT,               -- 0-21 (大牌)
    name_zh VARCHAR(50),      -- 愚者
    name_en VARCHAR(50),      -- The Fool
    keywords TEXT[],          -- 關鍵字
    upright_meaning TEXT,     -- 正位意義
    reversed_meaning TEXT,    -- 逆位意義
    image_url VARCHAR(255)
);

-- 牌陣
CREATE TABLE spreads (
    id SERIAL PRIMARY KEY,
    name_zh VARCHAR(50),      -- 三牌陣
    name_en VARCHAR(50),      -- Three Card Spread
    card_count INT,           -- 3
    positions JSONB,          -- [{position: 1, meaning: "過去"}, ...]
    suitable_questions TEXT[] -- 適合問題類型
);

-- 每週星象
CREATE TABLE weekly_horoscope (
    id SERIAL PRIMARY KEY,
    zodiac_id INT REFERENCES zodiac_signs(id),
    week_start DATE,
    week_end DATE,
    planetary_data JSONB,     -- 星象原始資料
    analysis TEXT,            -- AI 生成的分析
    created_at TIMESTAMP DEFAULT NOW()
);

-- 塔羅解讀紀錄
CREATE TABLE tarot_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spread_id INT REFERENCES spreads(id),
    question TEXT,
    cards_drawn JSONB,        -- 抽到的牌
    ai_interpretation TEXT,   -- AI 解讀
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 影響範圍

新專案，無既有檔案影響。

### 預計建立的檔案

**前端 (Vite + Vue 3)**
- `src/views/Home.vue` - 首頁
- `src/views/Horoscope.vue` - 星座運勢
- `src/views/Tarot.vue` - 塔羅抽牌
- `src/components/ZodiacCard.vue` - 星座卡片
- `src/components/TarotCard.vue` - 塔羅牌
- `src/components/SpreadLayout.vue` - 牌陣佈局

**後端 (FastAPI)**
- `app/main.py` - 主程式
- `app/routers/horoscope.py` - 星座運勢 API
- `app/routers/tarot.py` - 塔羅 API
- `app/services/astronomy.py` - 星曆計算
- `app/services/claude_ai.py` - Claude API 整合
- `app/models/` - SQLModel 資料模型

## UI/UX 規格

### 設計方向
- **風格**：親切日常、溫暖柔和
- **色彩**：深紫 + 金色點綴 + 米白背景
- **字型**：思源黑體（內文）、思源宋體（標題）

### 色彩系統
```css
:root {
  --primary: #4A3B6B;      /* 深紫 - 主色 */
  --secondary: #D4AF37;    /* 金色 - 強調 */
  --background: #FAF8F5;   /* 米白 - 背景 */
  --surface: #FFFFFF;      /* 白色 - 卡片 */
  --text: #2D2D2D;         /* 深灰 - 文字 */
  --text-muted: #6B6B6B;   /* 淺灰 - 次要文字 */
}
```

### 響應式
- Mobile: < 768px（單欄）
- Tablet: < 1024px（雙欄）
- Desktop: >= 1024px（三欄星座卡片）

## 測試計畫

1. **星曆計算**：比對 NASA Horizons 資料驗證準確度
2. **API 回應**：< 500ms
3. **AI 生成**：確認輸出為繁體中文、語氣親切
4. **前端載入**：首屏 < 2 秒

## 開發順序

1. 後端基礎 + Neon 連線
2. 星曆服務 + 行星位置 API
3. 前端專案 + 基本頁面
4. 塔羅牌資料 + 抽牌功能
5. Claude AI 整合
6. 每週自動生成排程

## Checklist

- [ ] 後端專案建置 (FastAPI)
- [ ] Neon 資料庫設定
- [ ] 星曆服務整合 (Skyfield)
- [ ] 前端專案建置 (Vite + Vue 3)
- [ ] 塔羅牌資料庫
- [ ] Claude API 整合
- [ ] 部署到 Render + Vercel
