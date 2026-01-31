---
title: 程式碼品質審查與修正
type: refactor
status: completed
created: 2026-01-31
completed: 2026-01-31
---

# 程式碼品質審查與修正

## 審查範圍

全面檢查違反開發規範的問題：
- 硬編碼 (Hardcoded values)
- 假資料 (Fake data)
- Mock 資料 (Fallback mock)
- UI/UX 設計規範

## 審查發現

### 1. 硬編碼 API URL（嚴重）

**問題**：前端 10 個檔案重複出現相同的 API URL fallback 模式：
```typescript
const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'
```

**影響檔案**：
- `frontend/src/views/HoroscopeView.vue:20`
- `frontend/src/views/StatsView.vue:27`
- `frontend/src/views/TarotReadingView.vue:38`
- `frontend/src/views/TarotView.vue:25`
- `frontend/src/views/HoroscopeDetailView.vue:104`
- `frontend/src/composables/useSukuyodo.ts:375`
- `frontend/src/views/SkyView.vue:71`
- `frontend/src/App.vue:16`
- `frontend/src/views/SukuyodoView.vue:271`
- `frontend/src/views/HomeView.vue:10`

**修正方案**：
- 建立 `frontend/src/config/api.ts` 統一管理 API URL
- 所有檔案改為 `import { apiUrl } from '@/config/api'`

### 2. 備用農曆算法（潛在風險）

**問題**：`backend/services/sukuyodo.py:94-120` 有 `_approximate_lunar` 備用方法

**分析**：
- 當 `lunarcalendar` 套件未安裝時啟用
- 此算法是近似值，可能有 1-2 天誤差
- 生產環境應確保 `lunarcalendar` 已安裝

**修正方案**：
- 確認 `requirements.txt` 已包含 `lunarcalendar`
- 加入啟動時檢查，若套件未安裝則拋出錯誤（而非使用備用算法）

### 3. 靜態配置資料（合規）

以下為天文/占星學固定規則，符合「靜態配置資料例外」：

| 檔案 | 資料 | 說明 |
|------|------|------|
| `ephemeris.py` | ZODIAC_SIGNS | 黃道十二宮定義 |
| `ephemeris.py` | PLANETS | 行星名稱對照 |
| `compatibility.py` | ELEMENT_COMPATIBILITY | 元素相性規則 |
| `compatibility.py` | SIGN_ELEMENTS | 星座元素對應 |
| `sukuyodo.py` | MONTH_START_MANSION | 月宿傍通曆（宗教典籍規則） |

**結論**：這些是占星術的固定計算規則，不是假資料，無需修改。

### 4. JSON 資料檔案（合規）

- `backend/data/sukuyodo_mansions.json` - 27 宿完整資料
- `backend/data/sukuyodo_fortune.json` - 運勢計算規則

**結論**：這是結構化的靜態配置，從 JSON 載入比硬編碼在程式碼中更好。

### 5. Mock/Fake 資料（未發現）

經過全面搜尋，未發現以下問題：
- 沒有 fallback mock 資料
- 沒有假資料返回
- 所有 API 都連接真實資料庫

## UI/UX 審查待執行

待使用以下 skill 進行審查：
- [ ] `/web-design-guidelines` - WCAG 合規性檢查
- [ ] `/ux-designer` - 設計規格審查

## 修正計畫

### Phase 1: API URL 統一化

1. 建立 `frontend/src/config/api.ts`
2. 修改 10 個檔案的 import

### Phase 2: 農曆套件檢查

1. 確認 `requirements.txt` 配置
2. 移除備用算法或改為錯誤拋出

### Phase 3: UI/UX 審查

1. 執行設計規範檢查
2. 修正發現的問題

## Checklist

- [x] 建立 `frontend/src/config/api.ts`
- [x] 修正 HoroscopeView.vue
- [x] 修正 StatsView.vue
- [x] 修正 TarotReadingView.vue
- [x] 修正 TarotView.vue
- [x] 修正 HoroscopeDetailView.vue
- [x] 修正 useSukuyodo.ts
- [x] 修正 SkyView.vue
- [x] 修正 App.vue
- [x] 修正 SukuyodoView.vue
- [x] 修正 HomeView.vue
- [x] 檢查 lunarcalendar 套件配置 (已在 requirements.txt)
- [x] 修改備用農曆算法為拋出錯誤
- [x] 執行 UI/UX 審查 (Web Interface Guidelines)
- [x] 修正 color-scheme: dark
- [x] 修正 scroll-behavior 尊重 reduced-motion
- [x] 修正 twinkle 動畫尊重 reduced-motion
- [x] 驗證建構成功
