# 月運勢與塔羅 AI 端點加輸入範圍與次數限制

- **title**: 月運勢與塔羅 AI 端點加輸入範圍與次數限制
- **type**: fix
- **status**: completed
- **完成日期**: 2026-11-14
- **建立日期**: 2026-11-14

## 背景

月運勢與塔羅解讀會呼叫付費的 AI 模型，這些端點不需登入，原本沒有輸入範圍與呼叫次數的限制。

## 變更內容

### 月運勢 `GET /api/horoscope/monthly/{code}`

- 原本的行為：`year`、`month` 接受任何整數，資料庫查不到就呼叫 AI 生成；生成失敗不留紀錄，同一組參數下次再呼叫一次。
- 現在的行為：
  - `year` 只接受今年前後各一年（今年 2026 時為 2025 到 2027），`month` 只接受 1 到 12，超出回 422，不查資料庫也不呼叫 AI。
    依據：前端只查當月；跨年時仍可查前一年 12 月與下一年 1 月。
  - 生成失敗的（星座、年、月）記在記憶體 10 分鐘，期間同一組參數直接回 404，不再呼叫 AI。生成成功就清掉紀錄。

### 塔羅

- 原本的行為：`POST /api/tarot/draw`、`POST /api/tarot/interpret`、`GET /api/tarot/ai-test` 沒有次數限制；
  `question` 與 `partner_nickname` 沒有長度上限；`/ai-test` 在任何環境都會呼叫 AI。
- 現在的行為：
  - 新增 `backend/services/rate_limit.py`：記憶體內計數、不新增相依。來源取 `X-Forwarded-For` 最後一段，沒有就用連線位址。
    每個來源每小時：抽牌 30 次、AI 解讀 10 次、AI 測試 5 次，超過回 429。
  - `DrawRequest.question` 上限 200 字，`CompatibilityContext.partner_nickname` 上限 50 字，超過回 422。
  - `/ai-test` 只有 `DEBUG=true` 時開放，其他環境回 404。這個端點前端沒有使用，只是除錯用。

## 影響範圍

- `backend/routers/horoscope.py`、`backend/routers/tarot.py`、`backend/models/tarot.py`、`backend/services/rate_limit.py`（新增）
- 計數存在單一行程的記憶體，重啟歸零；多個行程各自計。
- 前端塔羅問題輸入框沒有字數上限，超過 200 字送出會收到 422。

## UI 規格

無 UI 變更。

## 測試計畫

repo 沒有後端測試框架，用 FastAPI TestClient 跑實際 app（SQLite 記憶體資料庫、本機假 AI 上游、只允許連 loopback），比對改前與改後：

| 情境 | 改前 | 改後 |
|---|---|---|
| 6 組超出範圍的年月 | 200 ×6，AI 呼叫 6 次 | 422 ×6，AI 呼叫 0 次 |
| 合法年月、AI 回應無法解析，連打 3 次 | 404 ×3，AI 呼叫 3 次 | 404 ×3，AI 呼叫 1 次 |
| 當月、AI 正常，連打 3 次（對照） | 200 ×3，AI 呼叫 1 次 | 200 ×3，AI 呼叫 1 次 |
| `/ai-test` ×3 | 200 ×3，AI 呼叫 3 次 | 404 ×3，AI 呼叫 0 次；`DEBUG=true` 時 200 |
| 抽牌問題 201 字 / 200 字 / 暱稱 5000 字 | 200 / 200 / 200 | 422 / 200 / 422 |
| 同一來源抽牌加解讀 12 次（`X-Forwarded-For` 前段每次填不同值） | 200 ×12，AI 呼叫 12 次 | 200 ×10、429 ×2，AI 呼叫 10 次 |
| 另一個來源抽牌加解讀（對照） | 200 | 200 |
| 同一來源抽牌 35 次 | 200 ×35 | 200 ×30、429 ×5 |
