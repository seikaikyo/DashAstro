---
title: 宿曜道農曆西曆對照
type: feature
status: in-progress
created: 2026-01-25
---

# 宿曜道農曆西曆對照

## 需求來源

用戶反映：「對應農曆生日很難找吧！是不是可以搭配顯示西元年月日？」
用戶建議：±30 歲範圍

## 功能規格

### 顯示位置

在「尋找最佳配對」卡片中，每個相容星宿下方顯示對應的西曆生日範圍。

### 轉換邏輯

1. 根據星宿反推農曆月日
2. 將農曆月日轉換為多年的西曆日期
3. 範圍：當前年份 ±30 年（1996-2056）

### 資料結構

```
角宿（農曆 8/1）→
  1996: 9/13
  1997: 9/2
  1998: 9/21
  ...
```

---

## API 設計

擴展現有 `/compatibility-finder/{date_str}` 回應：

```json
{
  "best_matches": [
    {
      "mansion": "角宿",
      "lunar_dates": [
        {"month": 8, "day": 1}
      ],
      "solar_dates": [
        {"year": 2000, "date": "2000-09-28"},
        {"year": 2001, "date": "2001-09-17"},
        ...
      ]
    }
  ]
}
```

---

## 影響範圍

| 檔案 | 變更 |
|------|------|
| `backend/services/sukuyodo.py` | 新增農曆→西曆轉換 |
| `backend/routers/sukuyodo.py` | 擴展 API 回應 |
| `frontend/src/views/SukuyodoView.vue` | 顯示西曆日期 |

---

## Checklist

- [ ] 後端：農曆→西曆轉換函數
- [ ] 後端：擴展 compatibility-finder API
- [ ] 前端：顯示西曆日期列表
- [ ] 測試驗證
