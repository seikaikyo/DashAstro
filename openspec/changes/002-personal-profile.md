---
title: 個人檔案與配對分析
type: feature
status: in-progress
created: 2026-01-25
---

# 個人檔案與配對分析

## 變更內容

新增「我的收藏」功能，讓用戶可以：
1. 設定自己的性別和星座
2. 新增想關注的對象（性別 + 星座）
3. 在週運勢和塔羅占卜時，自動帶入配對分析

### 功能細節

**個人檔案**
- 我的性別：男/女/其他
- 我的星座：12 星座選擇
- 儲存於 localStorage（無需登入）

**關注對象**
- 可新增多個對象（最多 5 個）
- 每個對象設定：暱稱（選填）、性別、星座
- 可設定一個「主要對象」用於自動帶入

**配對分析整合**
| 功能 | 整合方式 |
|------|---------|
| 週運勢 | 感情運自動加入「與 XX 座的本週互動」分析 |
| 塔羅占卜 | 選擇「感情」相關牌陣時，自動帶入雙方星座 |
| AI 解讀 | Prompt 加入雙方星座，提供針對性建議 |

**星座配對邏輯**
- 元素相性：火+風和諧、土+水和諧
- 相位關係：同星座、對宮、三分相、四分相
- 結合當前天象：例如金星逆行對感情的影響

## 影響範圍

### 後端
| 檔案 | 變更 |
|------|------|
| `models/compatibility.py` | 新增配對分析模型 |
| `services/compatibility.py` | 星座配對計算邏輯 |
| `routers/compatibility.py` | 配對分析 API |
| `routers/horoscope.py` | 週運勢加入配對參數 |
| `services/claude_ai.py` | AI prompt 加入配對資訊 |

### 前端
| 檔案 | 變更 |
|------|------|
| `src/stores/profile.ts` | 個人檔案狀態管理 |
| `src/views/ProfileView.vue` | 個人設定頁面 |
| `src/components/ProfileSetup.vue` | 首次設定引導 |
| `src/components/PartnerSelector.vue` | 對象選擇元件 |
| `src/views/HoroscopeDetailView.vue` | 整合配對分析 |
| `src/views/TarotView.vue` | 感情牌陣帶入對象 |

### 資料庫
```sql
-- 配對分析紀錄（可選，用於 AI 快取）
CREATE TABLE compatibility_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zodiac1_code VARCHAR(3),
    zodiac2_code VARCHAR(3),
    week_start DATE,
    analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## UI/UX 規格

### 個人設定頁面 `/profile`
- 星空背景 + 卡片式設計
- 我的資料區塊：性別選擇 + 星座網格
- 關注對象區塊：列表 + 新增按鈕
- 儲存按鈕使用金色 `.btn-gold`

### 配對分析卡片
- 顯示在週運勢感情區塊下方
- 雙方星座符號 + 相性分數（1-5 星）
- 本週互動建議（約 50 字）

### 首次造訪引導
- 偵測 localStorage 無資料時顯示
- 簡單 3 步驟：選星座 → 選性別 → 完成
- 可跳過，之後在 header 提示設定

## 測試計畫

1. localStorage 存取正確
2. 配對 API 回傳正確相性分析
3. 週運勢頁面正確顯示配對資訊
4. 塔羅感情牌陣正確帶入對象
5. AI 解讀包含雙方星座分析

## Checklist
- [ ] 建立配對計算服務
- [ ] 建立配對 API
- [ ] 前端個人檔案頁面
- [ ] 整合週運勢
- [ ] 整合塔羅占卜
- [ ] 首次造訪引導
