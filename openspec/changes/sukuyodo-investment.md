---
title: 宿曜投資分析（私人功能）
type: feature
status: pending
trigger: manual
visibility: private
created: 2025-01-25
---

# 宿曜投資分析

> 私人功能，不對外公開。結合宿曜道與投資分析，供個人決策參考。

## 功能概述

將宿曜道的元素理論應用於投資分析：
- 本命宿元素 → 適合的投資風格與產業
- 農曆日期 → 進出場時機參考
- 流年運勢 → 年度投資策略

---

## Phase 1：本命宿投資屬性

### 七曜元素與投資風格

| 元素 | 特質 | 適合風格 | 適合產業 |
|------|------|---------|---------|
| **木** | 成長、擴張 | 成長股、長期持有 | 科技、綠能、教育 |
| **金** | 穩健、收斂 | 價值股、高股息 | 金融、礦業、精品 |
| **土** | 務實、累積 | 定期定額、不動產 | 營建、農業、基礎建設 |
| **日** | 領導、核心 | 權值股、ETF | 龍頭企業、指數型 |
| **月** | 變動、週期 | 波段操作 | 消費、零售、娛樂 |
| **火** | 積極、衝動 | 短線交易 | 軍工、能源、運動 |
| **水** | 靈活、流動 | 多元配置 | 航運、水資源、通訊 |

### API 設計

```
GET /api/sukuyodo/investment-profile/{date}
```

回應：
```json
{
  "mansion": "角宿",
  "element": "木",
  "investment_style": {
    "primary": "成長股",
    "secondary": "長期持有",
    "avoid": "短線殺進殺出"
  },
  "suitable_sectors": ["科技", "綠能", "教育"],
  "risk_tolerance": "中高",
  "holding_period": "中長期 (3-12 個月)"
}
```

---

## Phase 2：投資吉日選擇

### 結合一粒萬倍日

| 日期類型 | 適合操作 | 不適合操作 |
|---------|---------|-----------|
| 一粒萬倍日 + 大安 | 建倉、加碼、開戶 | 停損 |
| 一粒萬倍日 + 佛滅 | 觀望 | 大量交易 |
| 大安 | 穩健操作 | 高槓桿 |
| 赤口 | 僅正午前後操作 | 早盤晚盤 |

### 宿曜吉凶日

根據本命宿計算個人化吉凶：

```
GET /api/sukuyodo/investment-calendar?birth_date=1990-01-15&month=2025-02
```

回應：
```json
{
  "mansion": "心宿",
  "month": "2025-02",
  "days": [
    {
      "date": "2025-02-03",
      "lunar": "正月初六",
      "day_mansion": "箕宿",
      "relation": "栄親",
      "investment_rating": 5,
      "suggestion": "極佳交易日，適合重要決策"
    },
    {
      "date": "2025-02-04",
      "lunar": "正月初七",
      "day_mansion": "斗宿",
      "relation": "安壊",
      "investment_rating": 2,
      "suggestion": "避免大額交易，觀望為主"
    }
  ]
}
```

### 日宿計算邏輯

每日的「值日宿」根據農曆日期循環：
- 農曆初一 → 該月起始宿
- 每日進一宿
- 與本命宿的關係決定吉凶

---

## Phase 3：與 DashTrade 整合

### 整合方式

1. DashTrade 呼叫 DashAstro API 取得個人化吉日
2. 在技術分析結果上疊加宿曜建議
3. 僅在登入狀態下顯示（私人功能）

### 顯示位置

```
DashTrade 技術分析結果
├── DashAI 分數：75（偏多）
├── Antigravity 分數：68
├── 技術指標：RSI 55, MACD 金叉
│
└── [私人] 宿曜參考
    ├── 今日值日宿：箕宿（與你的心宿為栄親）
    ├── 投資評級：★★★★★
    └── 建議：適合加碼，吉日
```

### 環境變數

```
# DashTrade 後端
DASHASTRO_API_URL=https://dashastro-api.onrender.com
SUKUYODO_ENABLED=true
USER_BIRTH_DATE=1990-01-15  # 你的生日（私密）
```

---

## 資料庫變更

```sql
-- 個人設定表（私密）
CREATE TABLE user_sukuyodo_settings (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) UNIQUE,
  birth_date DATE NOT NULL,
  show_in_analysis BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 影響範圍

### DashAstro
| 檔案 | 變更 |
|------|------|
| `services/sukuyodo.py` | 新增投資屬性計算 |
| `routers/sukuyodo.py` | 新增私人 API |
| `data/sukuyodo_investment.json` | 元素與產業對照表 |

### DashTrade
| 檔案 | 變更 |
|------|------|
| `services/sukuyodo_integration.py` | 整合 DashAstro API |
| `routers/analysis.py` | 疊加宿曜建議 |
| `frontend/components/SukuyodoHint.vue` | 顯示元件 |

---

## 安全考量

1. **不公開** - 此功能不對外宣傳
2. **不做保證** - 僅供參考，不構成投資建議
3. **生日保護** - 個人生日資料加密儲存
4. **API 認證** - 私人 API 需要驗證

---

## Checklist

### Phase 1（本命宿投資屬性）
- [ ] 建立元素與產業對照表
- [ ] 實作 investment-profile API
- [ ] 測試準確性

### Phase 2（投資吉日）
- [ ] 實作日宿計算邏輯
- [ ] 實作 investment-calendar API
- [ ] 與一粒萬倍日整合

### Phase 3（DashTrade 整合）
- [ ] DashTrade 呼叫 DashAstro API
- [ ] 前端顯示元件
- [ ] 私密設定頁面

---

## 備註

- 此功能為個人工具，不對外商業化
- 宿曜道僅供參考，投資決策仍需結合技術分析
- 可依實際使用經驗持續調整元素與產業對照
