---
title: 宿曜道運勢模組 - 日/週/月/年運勢
type: feature
status: planning
created: 2025-01-25
---

# 宿曜道運勢模組

## 需求概述

基於本命宿，提供多時間尺度的運勢預測：
- 每日運勢（七曜日運）
- 每週運勢（七曜週期）
- 每月運勢（行度宿）
- 每年運勢（流年神煞）

並細分為：事業運、感情運、健康運、財運

---

## Phase 1: 每日運勢（七曜日運）

### 原理

每個本命宿對應一個七曜（日月火水木金土），每天也對應一個七曜：
- 日曜日（週日）、月曜日（週一）、火曜日（週二）...

當「本命宿的七曜」與「當日七曜」相合時，該日較為順利。

### 計算邏輯

```python
# 本命宿的七曜對應
MANSION_TO_ELEMENT = {
    "角宿": "木", "亢宿": "金", "氐宿": "土", "房宿": "日", "心宿": "月",
    "尾宿": "火", "箕宿": "水", "斗宿": "木", "牛宿": "金", "女宿": "土",
    # ... 全部 27 宿
}

# 七曜相生關係
GENERATING = [("木", "火"), ("火", "土"), ("土", "金"), ("金", "水"), ("水", "木")]
SAME_ELEMENT_BONUS = 20      # 同元素
GENERATING_BONUS = 10        # 相生
NEUTRAL = 0                  # 無關
CONFLICTING_PENALTY = -10    # 相剋

def calculate_daily_fortune(mansion_element: str, day_element: str) -> int:
    if mansion_element == day_element:
        return SAME_ELEMENT_BONUS
    if (mansion_element, day_element) in GENERATING:
        return GENERATING_BONUS
    # ... 相剋計算
```

### API 設計

```
GET /api/sukuyodo/fortune/daily/{date_str}
Query: ?birth_date=1977-10-29

Response:
{
  "date": "2025-01-25",
  "day_element": "土",
  "day_element_reading": "ど",
  "your_mansion": "畢宿",
  "your_element": "月",
  "fortune": {
    "overall": 75,
    "career": 70,
    "love": 80,
    "health": 65,
    "wealth": 72
  },
  "advice": "今日土曜與月曜相生，適合穩定發展...",
  "lucky": {
    "direction": "西南",
    "color": "黃色",
    "number": 5
  }
}
```

---

## Phase 2: 每月運勢（行度宿）

### 原理

每個農曆月份有一個「月宿」（月亮在該月主要停留的宿位）。
本命宿與當月月宿的關係，決定該月運勢。

### 計算邏輯

```python
# 農曆月份對應的主要月宿（簡化版）
MONTH_MANSION = {
    1: 11,   # 正月：危宿
    2: 13,   # 二月：壁宿
    # ... 同月宿傍通曆
}

def calculate_monthly_fortune(user_mansion_index: int, lunar_month: int) -> dict:
    month_mansion = MONTH_MANSION[lunar_month]
    relation = get_relation_type(user_mansion_index, month_mansion)

    # 根據關係類型給出運勢
    if relation == "eishin":  # 榮親
        return {"level": "大吉", "score": 95, "advice": "本月萬事順利..."}
    elif relation == "ankai":  # 安壊
        return {"level": "小凶", "score": 45, "advice": "本月宜低調..."}
    # ...
```

### API 設計

```
GET /api/sukuyodo/fortune/monthly/{year}/{month}
Query: ?birth_date=1977-10-29

Response:
{
  "year": 2025,
  "month": 1,
  "lunar_month": 12,
  "month_mansion": "女宿",
  "your_mansion": "畢宿",
  "relation": "友衰",
  "fortune": {
    "overall": 70,
    "career": 65,
    "love": 75,
    "health": 70,
    "wealth": 68
  },
  "weekly_breakdown": [
    {"week": 1, "score": 72, "focus": "事業"},
    {"week": 2, "score": 68, "focus": "健康"},
    {"week": 3, "score": 75, "focus": "感情"},
    {"week": 4, "score": 70, "focus": "財運"}
  ],
  "advice": "本月為友衰月，適合與朋友相處但要避免耍廢..."
}
```

---

## Phase 3: 每年運勢（流年神煞）

### 原理

基於農曆年的天干地支，計算與本命宿的關係：
- 太歲：該年的主宰星
- 歲破：與太歲對沖的方位
- 三煞：該年不利的方位

### 計算邏輯

```python
# 天干地支對應的宿位影響
ZODIAC_MANSION_RELATION = {
    "子": [9, 10, 11],   # 鼠年影響的宿位
    "丑": [12, 13, 14],  # 牛年影響的宿位
    # ...
}

def calculate_yearly_fortune(user_mansion_index: int, year: int) -> dict:
    zodiac = get_zodiac(year)  # 取得該年生肖
    affected = ZODIAC_MANSION_RELATION[zodiac]

    if user_mansion_index in affected:
        return {"warning": "犯太歲", "advice": "宜安太歲..."}
    # ...
```

### API 設計

```
GET /api/sukuyodo/fortune/yearly/{year}
Query: ?birth_date=1977-10-29

Response:
{
  "year": 2025,
  "zodiac": "蛇",
  "zodiac_reading": "へび",
  "heavenly_stem": "乙",
  "earthly_branch": "巳",
  "your_mansion": "畢宿",
  "fortune": {
    "overall": 78,
    "career": 82,
    "love": 75,
    "health": 72,
    "wealth": 80
  },
  "monthly_trend": [
    {"month": 1, "score": 70},
    {"month": 2, "score": 75},
    // ... 12 個月
  ],
  "warnings": [],
  "opportunities": ["三月適合求職", "七月財運旺"],
  "advice": "乙巳年對畢宿而言是穩定發展的一年..."
}
```

---

## Phase 4: 前端 UI

### 頁面結構

```
SukuyodoView.vue（現有）
├── 本命宿查詢（現有）
├── 相性配對查詢（現有）
└── 運勢查詢（新增）
    ├── Tab: 今日運勢
    ├── Tab: 本月運勢
    └── Tab: 本年運勢

或獨立頁面：
FortuneView.vue
├── 運勢總覽卡片（今日/本週/本月/本年）
├── 詳細運勢區塊
│   ├── 事業運
│   ├── 感情運
│   ├── 健康運
│   └── 財運
├── 幸運指南（方位/顏色/數字）
└── 運勢趨勢圖（折線圖）
```

### UI 元件

- 圓形進度條顯示分數
- 五星/十分制評分
- 月曆熱力圖顯示每日運勢
- 趨勢折線圖顯示月度走勢

---

## 影響範圍

| 檔案 | 變更 |
|------|------|
| `backend/data/sukuyodo_fortune.json` | 新增運勢描述資料 |
| `backend/services/sukuyodo.py` | 新增運勢計算方法 |
| `backend/routers/sukuyodo.py` | 新增運勢 API 端點 |
| `frontend/src/views/SukuyodoView.vue` | 新增運勢區塊 |
| `frontend/src/views/FortuneView.vue` | 新增（可選）|
| `frontend/src/router/index.ts` | 新增路由（如有獨立頁面）|

---

## 實作順序

1. **Phase 1: 每日運勢** - 最基本，計算簡單
2. **Phase 2: 每月運勢** - 擴充月度視角
3. **Phase 3: 每年運勢** - 需要研究流年神煞
4. **Phase 4: 前端整合** - UI 優化

---

## Checklist

### Phase 1（每日）
- [ ] 建立七曜對照資料
- [ ] 實作每日運勢計算
- [ ] 新增 API 端點
- [ ] 前端顯示今日運勢

### Phase 2（每月）
- [ ] 建立月宿對照資料
- [ ] 實作月運勢計算（含週分解）
- [ ] 新增 API 端點
- [ ] 前端顯示本月運勢

### Phase 3（每年）
- [ ] 研究《宿曜經》流年神煞
- [ ] 建立年運勢計算邏輯
- [ ] 新增 API 端點
- [ ] 前端顯示本年運勢

### Phase 4（UI）
- [ ] 運勢總覽卡片
- [ ] 趨勢圖表
- [ ] 幸運指南
- [ ] RWD 優化

---

## 商業化考量

- 基礎運勢（今日）：免費
- 詳細運勢（週/月/年）：付費功能
- 個人化建議：訂閱制
