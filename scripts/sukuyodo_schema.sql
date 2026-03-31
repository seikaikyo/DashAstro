-- 宿曜道資料表 Schema
-- 建立於 2026-01-31

-- 1. 二十七宿/二十八宿基本資料
CREATE TABLE IF NOT EXISTS sukuyodo_mansions (
    id SERIAL PRIMARY KEY,
    index_num INTEGER NOT NULL UNIQUE,
    name_jp VARCHAR(10) NOT NULL,
    name_zh VARCHAR(10) NOT NULL,
    reading VARCHAR(20) NOT NULL,
    element VARCHAR(5) NOT NULL,
    element_animal VARCHAR(10),
    quadrant VARCHAR(20),
    quadrant_element VARCHAR(5),
    personality TEXT,
    keywords TEXT[],
    love TEXT,
    career TEXT,
    health TEXT,
    is_excluded_jp BOOLEAN DEFAULT FALSE,
    is_excluded_cn BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 月宿傍通曆（各月起始宿）
CREATE TABLE IF NOT EXISTS sukuyodo_month_start (
    id SERIAL PRIMARY KEY,
    lunar_month INTEGER NOT NULL UNIQUE CHECK (lunar_month BETWEEN 1 AND 12),
    start_mansion_index INTEGER NOT NULL,
    start_mansion_name VARCHAR(10) NOT NULL,
    verification_status VARCHAR(20) DEFAULT 'pending',
    verification_source TEXT,
    verified_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 關係類型定義
CREATE TABLE IF NOT EXISTS sukuyodo_relations (
    id SERIAL PRIMARY KEY,
    type_key VARCHAR(20) NOT NULL UNIQUE,
    name_zh VARCHAR(10) NOT NULL,
    name_jp VARCHAR(10) NOT NULL,
    reading VARCHAR(20) NOT NULL,
    distances INTEGER[] NOT NULL,
    base_score INTEGER NOT NULL,
    description TEXT,
    detailed TEXT,
    advice TEXT,
    tips TEXT[],
    avoid_actions TEXT[],
    good_for TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 距離類型定義（完整版）
CREATE TABLE IF NOT EXISTS sukuyodo_distance_types (
    id SERIAL PRIMARY KEY,
    relation_key VARCHAR(20) NOT NULL,
    distance_type VARCHAR(10) NOT NULL CHECK (distance_type IN ('near', 'mid', 'far')),
    distances INTEGER[] NOT NULL,
    direction VARCHAR(10),
    description TEXT,
    intensity_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(relation_key, distance_type, direction)
);

-- 5. 五行關係
CREATE TABLE IF NOT EXISTS sukuyodo_five_elements (
    id SERIAL PRIMARY KEY,
    element1 VARCHAR(5) NOT NULL,
    element2 VARCHAR(5) NOT NULL,
    relation_type VARCHAR(20) NOT NULL CHECK (relation_type IN ('generating', 'conflicting', 'weakening', 'same', 'neutral')),
    bonus_score INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(element1, element2)
);

-- 6. 七曜元素
CREATE TABLE IF NOT EXISTS sukuyodo_weekday_elements (
    id SERIAL PRIMARY KEY,
    weekday_num INTEGER NOT NULL UNIQUE CHECK (weekday_num BETWEEN 0 AND 6),
    name_jp VARCHAR(10) NOT NULL,
    reading VARCHAR(20) NOT NULL,
    element VARCHAR(5) NOT NULL,
    planet_zh VARCHAR(10) NOT NULL,
    planet_sanskrit VARCHAR(20),
    energy VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 計算公式文檔
CREATE TABLE IF NOT EXISTS sukuyodo_formulas (
    id SERIAL PRIMARY KEY,
    formula_key VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(30) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    formula_text TEXT NOT NULL,
    formula_python TEXT,
    variables JSONB,
    examples JSONB,
    source TEXT,
    verification_status VARCHAR(20) DEFAULT 'verified',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 驗證記錄
CREATE TABLE IF NOT EXISTS sukuyodo_verification_log (
    id SERIAL PRIMARY KEY,
    target_type VARCHAR(30) NOT NULL,
    target_key VARCHAR(50) NOT NULL,
    verification_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    source TEXT,
    source_url TEXT,
    notes TEXT,
    verified_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_mansions_element ON sukuyodo_mansions(element);
CREATE INDEX IF NOT EXISTS idx_relations_type ON sukuyodo_relations(type_key);
CREATE INDEX IF NOT EXISTS idx_formulas_category ON sukuyodo_formulas(category);
CREATE INDEX IF NOT EXISTS idx_verification_target ON sukuyodo_verification_log(target_type, target_key);
