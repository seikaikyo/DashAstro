-- DashAstro 星語塔羅 - 資料庫 Schema
-- 執行位置：Neon Console (https://console.neon.tech)
-- 專案：建立新專案 dashastro 或在現有專案中執行

-- 星座基本資料
CREATE TABLE IF NOT EXISTS zodiac_signs (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) UNIQUE NOT NULL,
    name_zh VARCHAR(10) NOT NULL,
    name_en VARCHAR(20) NOT NULL,
    symbol VARCHAR(5) NOT NULL,
    element VARCHAR(10) NOT NULL,
    modality VARCHAR(10) NOT NULL,
    ruling_planet VARCHAR(20) NOT NULL,
    date_start VARCHAR(5) NOT NULL,
    date_end VARCHAR(5) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 塔羅牌
CREATE TABLE IF NOT EXISTS tarot_cards (
    id SERIAL PRIMARY KEY,
    number INT UNIQUE NOT NULL,
    name_zh VARCHAR(50) NOT NULL,
    name_en VARCHAR(50) NOT NULL,
    keywords TEXT[] NOT NULL,
    upright_meaning TEXT NOT NULL,
    reversed_meaning TEXT NOT NULL,
    image_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 牌陣
CREATE TABLE IF NOT EXISTS tarot_spreads (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name_zh VARCHAR(50) NOT NULL,
    description TEXT,
    card_count INT NOT NULL,
    positions JSONB NOT NULL,
    suitable_questions TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 每週星座運勢
CREATE TABLE IF NOT EXISTS weekly_horoscope (
    id SERIAL PRIMARY KEY,
    zodiac_id INT REFERENCES zodiac_signs(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    summary TEXT NOT NULL,
    love_advice TEXT,
    career_advice TEXT,
    health_advice TEXT,
    lucky_day VARCHAR(10),
    lucky_color VARCHAR(20),
    lucky_number INT,
    overall_score INT CHECK (overall_score BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(zodiac_id, week_start)
);

-- 塔羅解讀紀錄
CREATE TABLE IF NOT EXISTS tarot_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spread_id INT REFERENCES tarot_spreads(id),
    question TEXT,
    cards_drawn JSONB NOT NULL,
    ai_interpretation TEXT,
    session_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_weekly_horoscope_week ON weekly_horoscope(week_start);
CREATE INDEX IF NOT EXISTS idx_tarot_readings_created ON tarot_readings(created_at);
CREATE INDEX IF NOT EXISTS idx_tarot_readings_session ON tarot_readings(session_id);
