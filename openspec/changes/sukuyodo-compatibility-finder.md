---
title: 宿曜道相性配對查詢功能
type: feature
status: in-progress
created: 2025-01-25
---

# 宿曜道相性配對查詢功能

## 需求

輸入自己的生日後，自動列出：
1. **榮親（えいしん）** - 最適合結婚的本命宿（95 分）
2. **業胎（ぎょうたい）** - 前世之緣的本命宿（90 分）
3. **安壊（あんかい）** - 需要注意避免的本命宿（55 分）

---

## 技術設計

### 新增 API 端點

```
GET /api/sukuyodo/compatibility-finder/{date_str}
```

**回傳格式：**
```json
{
  "success": true,
  "data": {
    "your_mansion": {
      "name_jp": "畢宿",
      "reading": "ひつしゅく",
      "index": 18,
      "element": "月"
    },
    "best_for_marriage": [
      {
        "name_jp": "亢宿",
        "reading": "こうしゅく",
        "index": 1,
        "element": "金",
        "relation": "榮親",
        "score": 95
      }
    ],
    "past_life_connection": [...],
    "should_avoid": [...]
  }
}
```

### 計算邏輯

根據用戶的本命宿 index，計算各關係類型的配對宿位：

```python
def find_compatible_mansions(user_index: int) -> dict:
    RELATIONS = {
        "eishin": {"name": "榮親", "distances": [1, 3, 10, 12, 15, 17, 24, 26], "score": 95},
        "gyotai": {"name": "業胎", "distances": [9, 18], "score": 90},
        "ankai": {"name": "安壊", "distances": [4, 6, 21, 23], "score": 55}
    }

    result = {}
    for key, rel in RELATIONS.items():
        indices = set()
        for d in rel["distances"]:
            indices.add((user_index + d) % 27)
            indices.add((user_index - d + 27) % 27)
        result[key] = list(indices)

    return result
```

---

## 前端設計

### UI 位置

在查詢本命宿結果下方，新增「尋找配對」區塊

### 呈現方式

```
┌─────────────────────────────────────┐
│  🔍 尋找你的最佳配對                 │
├─────────────────────────────────────┤
│  你的本命宿：畢宿（ひつしゅく）        │
│                                     │
│  💍 最適合結婚（榮親・えいしん）95分   │
│  ┌──────┬──────┬──────┬──────┐      │
│  │ 亢宿 │ 房宿 │ 箕宿 │ 牛宿 │      │
│  │ 婁宿 │ 昴宿 │ 觜宿 │ 井宿 │      │
│  └──────┴──────┴──────┴──────┘      │
│                                     │
│  🔮 前世之緣（業胎・ぎょうたい）90分   │
│  ┌──────┬──────┐                    │
│  │ 角宿 │ 女宿 │                    │
│  └──────┴──────┘                    │
│                                     │
│  ⚠️ 需要小心（安壊・あんかい）55分    │
│  ┌──────┬──────┬──────┬──────┐      │
│  │ 室宿 │ 奎宿 │ 鬼宿 │ 星宿 │      │
│  └──────┴──────┴──────┴──────┘      │
└─────────────────────────────────────┘
```

### 互動

- 點擊任一宿名可展開查看該宿的詳細性格描述
- 顯示月宿傍通曆，讓用戶知道哪些農曆生日對應這些宿位

---

## 影響範圍

| 檔案 | 變更 |
|------|------|
| `backend/services/sukuyodo.py` | 新增 `find_compatible_mansions()` 方法 |
| `backend/routers/sukuyodo.py` | 新增 `/compatibility-finder/{date}` 端點 |
| `frontend/src/views/SukuyodoView.vue` | 新增相性配對區塊 |

---

## Checklist

- [ ] 後端新增 `find_compatible_mansions()` 方法
- [ ] 後端新增 API 端點
- [ ] 前端新增 UI 區塊
- [ ] 測試驗證計算正確性
