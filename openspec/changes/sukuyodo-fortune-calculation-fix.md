---
title: 修正宿曜道運勢計算公式
type: fix
status: completed
priority: critical
created: 2026-01-26
---

# 修正宿曜道運勢計算公式

## 問題描述

目前運勢計算存在嚴重邏輯錯誤，導致幾乎不會出現「凶」的結果：

1. **基礎分數過高**：固定從 70 分起算
2. **缺少關鍵計算**：沒有計算「當日宿」與「本命宿」的三九秘法關係
3. **僅用七曜元素**：只用星期幾的元素加減分，而非真正的宿曜關係

### 當前錯誤邏輯

```python
# 基礎分數 (60-80) - 錯！固定太高
base_score = 70

# 僅根據七曜元素調整 - 錯！應該用宿曜關係
overall_score = max(30, min(100, base_score + base_bonus))
```

實際分數範圍：52~98 分（幾乎都是「吉」以上）

## 正確的宿曜道運勢計算

### 三九秘法核心原理

傳統宿曜道中，每日運勢的核心是「當日宿」與「本命宿」的關係：

| 關係類型 | 距離 | 運勢等級 | 分數範圍 |
|---------|------|---------|---------|
| 榮親 | 1,3,10,12,15,17,24,26 | 大吉 | 85-95 |
| 業胎 | 9, 18 | 吉 | 80-90 |
| 命 | 0 | 中吉 | 75-85 |
| 友衰 | 2,5,11,13,14,16,22,25 | 中吉 | 65-75 |
| 危成 | 7,8,19,20 | 小吉 | 50-65 |
| 安壞 | 4,6,21,23 | 凶 | 35-50 |

### 修正後的計算公式

```python
def calculate_daily_fortune(self, birth_date: date, target_date: date) -> dict:
    # 1. 取得本命宿
    user_mansion = self.get_mansion(birth_date)
    user_index = user_mansion["index"]

    # 2. 計算「當日宿」（根據目標日期的農曆）
    lunar_y, lunar_m, lunar_d, _ = self.solar_to_lunar(target_date)
    day_mansion_index = self.get_mansion_index(lunar_m, lunar_d)

    # 3. 計算三九秘法關係
    relation = self.get_relation_type(user_index, day_mansion_index)
    relation_type = relation["type"]

    # 4. 根據關係類型決定基礎分數
    BASE_SCORES = {
        "榮親": (85, 95),   # 大吉
        "業胎": (80, 90),   # 吉
        "命": (75, 85),     # 中吉
        "友衰": (65, 75),   # 中吉
        "危成": (50, 65),   # 小吉
        "安壞": (35, 50),   # 凶
    }

    score_range = BASE_SCORES.get(relation_type, (60, 75))
    base_score = random.randint(score_range[0], score_range[1])

    # 5. 七曜元素微調（次要因素）
    element_bonus = self._calc_element_adjustment(user_element, day_element)
    overall_score = max(30, min(100, base_score + element_bonus))
```

## 影響範圍

| 檔案 | 變更類型 |
|------|----------|
| `backend/services/sukuyodo.py` | 修改 `calculate_daily_fortune()` |
| `backend/services/sukuyodo.py` | 修改 `calculate_weekly_fortune()` |
| `backend/services/sukuyodo.py` | 修改 `calculate_monthly_fortune()` |
| `backend/data/sukuyodo_fortune.json` | 新增關係-分數對照表（可選） |

## UI 判斷邏輯（前端）

目前前端判斷正確，不需修改：

```typescript
// frontend/src/views/SukuyodoView.vue:781-785
const getFortuneLevel = (score: number) => {
  if (score >= 90) return { text: '大吉', class: 'excellent' }
  if (score >= 75) return { text: '吉', class: 'good' }
  if (score >= 60) return { text: '中吉', class: 'fair' }
  if (score >= 45) return { text: '小吉', class: 'caution' }
  return { text: '凶', class: 'poor' }
}
```

## Checklist

- [x] 修改 `calculate_daily_fortune()` 加入當日宿計算
- [x] 根據三九秘法關係決定基礎分數
- [x] 將七曜元素改為次要微調因素
- [x] 前端新增當日宿關係顯示
- [ ] 更新 `calculate_weekly_fortune()` 同步邏輯（可選）
- [ ] 測試各種關係類型的分數分佈
