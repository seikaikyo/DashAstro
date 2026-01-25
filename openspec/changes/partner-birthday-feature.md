---
title: 收藏對象新增生日欄位
type: feature
status: in-progress
created: 2026-01-25
---

# 收藏對象新增生日欄位

## 需求背景

用戶希望能對收藏的對象使用宿曜道運勢預測功能，但目前 `Partner` 資料結構缺少生日欄位。

## 變更內容

### 1. 資料結構擴充

```typescript
interface Partner {
  id: string
  nickname: string
  gender: 'male' | 'female' | 'other'
  zodiacCode: string
  isPrimary: boolean
  birthDate?: string  // 新增：YYYY-MM-DD 格式
}
```

### 2. 前端 UI 修改

**ProfileView.vue - 新增對象表單**
- 新增日期選擇器欄位
- 生日為選填（向下相容舊資料）
- 自動從生日推算星座（可覆蓋）

**SukuyodoView.vue - 整合收藏對象**
- 本命宿查詢可選擇收藏對象（有生日者）
- 相性診斷可直接選擇雙方

### 3. 向下相容

- 既有收藏資料中 `birthDate` 為 undefined，正常運作
- 新增對象時生日為選填
- 有生日的對象才能使用宿曜道功能

---

## 影響範圍

| 檔案 | 變更 |
|------|------|
| `frontend/src/stores/profile.ts` | Partner 介面新增 birthDate |
| `frontend/src/views/ProfileView.vue` | 新增/編輯對象表單加入日期選擇器 |
| `frontend/src/views/SukuyodoView.vue` | 整合收藏對象選擇 |

---

## UI 規格

### ProfileView - 新增對象表單

```
┌─────────────────────────────────────────┐
│ 新增關注對象                            │
├─────────────────────────────────────────┤
│ 暱稱                                    │
│ [________________]                       │
│                                         │
│ 生日（選填）                            │
│ [____年____月____日]                    │
│ ℹ️ 填寫生日可使用宿曜道運勢預測          │
│                                         │
│ 性別                                    │
│ (•) 男  ( ) 女  ( ) 其他               │
│                                         │
│ 星座                                    │
│ [下拉選單 / 如有生日可自動選擇]         │
│                                         │
│ [取消]                    [新增]        │
└─────────────────────────────────────────┘
```

### SukuyodoView - 收藏對象選擇

```
┌─────────────────────────────────────────┐
│ 快速選擇收藏對象                        │
├─────────────────────────────────────────┤
│ [小明 ♈]  [小美 ♌]  [+新增對象]         │
└─────────────────────────────────────────┘
```

- 僅顯示有填寫生日的收藏對象
- 點擊後自動填入生日並查詢

---

## 實作順序

1. 修改 `profile.ts` - 新增 birthDate 欄位
2. 修改 `ProfileView.vue` - UI 新增日期輸入
3. 修改 `SukuyodoView.vue` - 整合收藏對象選擇

---

## Checklist

- [x] `frontend/src/stores/profile.ts` 新增 birthDate 欄位
- [x] `frontend/src/views/ProfileView.vue` 新增日期選擇 UI
- [x] `frontend/src/views/SukuyodoView.vue` 整合收藏對象快速選擇
- [ ] 測試向下相容（舊資料無生日仍可運作）
