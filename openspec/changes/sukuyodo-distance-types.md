---
title: 宿曜道距離類型系統
type: feature
status: completed
created: 2026-01-31
completed: 2026-01-31
phase: 1
---

# 宿曜道距離類型系統

## 變更內容

在相性分析中加入「近距離/中距離/遠距離」判定，並區分「榮/親」「安/壞」等關係的方向性。

## 功能說明

### 距離類型

| 類型 | 日文 | 說明 | 影響強度 |
|------|------|------|----------|
| 近距離 | 近距離 | 關係特徵最強烈 | 100% |
| 中距離 | 中距離 | 關係最為平衡（戀愛最佳） | 90% |
| 遠距離 | 遠距離 | 關係特徵較淡 | 75% |

### 方向性（榮/親為例）

- **栄（えい）**：我對對方有利，給予繁榮
- **親（しん）**：對方對我有利，受惠親愛

## 影響範圍

- `backend/services/sukuyodo.py`
- `backend/data/sukuyodo_mansions.json`
- `frontend/src/composables/useSukuyodo.ts`
- `frontend/src/components/sukuyodo/MatchTab.vue`

## UI/UX 規格

### 相性結果卡片新增顯示

```
┌─────────────────────────────────────┐
│ 關係類型：榮親                       │
│ 距離類型：近距離                     │  ← 新增
│ 方向性：你是「栄」/ 對方是「親」      │  ← 新增
│ 相性分數：95 分                      │
└─────────────────────────────────────┘
```

### 距離類型標籤樣式

- 近距離：紅色標籤 `--sl-color-danger-500`
- 中距離：綠色標籤 `--sl-color-success-500`
- 遠距離：灰色標籤 `--sl-color-neutral-500`

## 測試計畫

1. 單元測試：距離類型計算正確性
2. 方向性判定：確認榮/親、安/壞方向正確
3. UI 測試：標籤正確顯示

## Checklist

- [x] 後端：新增 `DISTANCE_TYPE_MAP` 常數
- [x] 後端：新增 `_get_distance_info()` 輔助方法
- [x] 後端：新增 `_get_distance_type_name()` 輔助方法
- [x] 後端：更新 `get_relation_type()` 回傳距離類型和方向
- [x] 後端：更新 `calculate_compatibility()` 回應格式
- [x] 前端：更新 `useSukuyodo.ts` Relation 型別定義
- [x] 前端：更新 `MatchTab.vue` 顯示距離標籤和方向性
- [x] 前端：新增距離標籤 CSS 樣式
- [x] 驗證：後端語法正確、前端無新錯誤
