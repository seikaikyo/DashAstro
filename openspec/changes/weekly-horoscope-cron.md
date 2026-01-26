---
title: 週運勢自動生成 Cron Job
type: feature
status: completed
created: 2026-01-26
---

# 週運勢自動生成 Cron Job

## 變更內容

建立自動生成週運勢的機制：
1. 在 DashAstro 後端新增 `/api/cron/generate-weekly-horoscope` 端點
2. 呼叫 `claude_service.generate_weekly_horoscope()` 為 12 個星座生成週運勢
3. 將結果存入 `weekly_horoscope` 資料表
4. 由 `dashtrade-scheduler` Cron Job 每週一呼叫

## 影響範圍

### DashAstro 後端
- `backend/routers/cron.py` - 新增生成端點
- `backend/models/horoscope.py` - 確認 WeeklyHoroscope model

### DashTrade Scheduler
- `backend/cron_tasks.py` - 新增 `generate_dashastro_weekly_horoscope()` 函數

## 技術設計

### API 端點
```
POST /api/cron/generate-weekly-horoscope
Header: X-Cron-Secret: {CRON_SECRET}
Response: { success: true, data: { generated: 12, week_start: "2026-01-27" } }
```

### 執行邏輯
1. 計算本週一日期 (`week_start`)
2. 檢查是否已有該週資料（避免重複生成）
3. 遍歷 12 個星座，呼叫 Claude AI 生成內容
4. 存入 `weekly_horoscope` 資料表

### 排程時機
- 在 `dashtrade-scheduler` 的 Phase 6 後新增
- 每週一早上 08:00 (台灣時間) 執行
- 條件：`weekday() == 0 and tw_hour == 8`

## 測試計畫

1. 本機測試 API 端點
   ```bash
   curl -X POST http://localhost:8000/api/cron/generate-weekly-horoscope
   ```

2. 驗證資料庫寫入
   ```bash
   curl https://dashastro-api.onrender.com/api/horoscope/weekly/SCO
   ```

3. 驗證前端顯示正確

## Checklist

- [x] DashAstro: 新增 `/api/cron/generate-weekly-horoscope` 端點
- [x] DashAstro: 實作生成邏輯（查星座 → AI 生成 → 存 DB）
- [x] DashTrade: 新增 `generate_dashastro_weekly_horoscope()` 函數
- [x] DashTrade: 在 `run_scheduled_tasks()` 加入呼叫
- [x] 測試完整流程
- [x] 推送並驗證
