# 呼叫 Claude API 的回應處理照官方文件修正

- **type**: fix
- **建立日期**: 2026-11-19
- **status**: in-progress

## 背景

2026-11-19 對照 Claude 平台官方文件，backend 四個呼叫 Claude 的地方都有同樣兩個問題：

1. 直接讀 `response.content[0].text`。Opus 5、Sonnet 5 以後沒帶 thinking 也會先思考，第一塊可能是 thinking（官方 build-with-claude/prompt-engineering/claude-prompting-best-practices.md:779），換模型後塔羅解讀、週運勢、月運勢全部會失敗。
2. 沒讀 `stop_reason`。拒答是 HTTP 200 加 `stop_reason: "refusal"`（handling-stop-reasons.md:1783）；思考算進 `max_tokens`（models/fable-5-2/migration-guide.md:95）。現在拒答的文字會被當成塔羅解讀存進快取，被截斷但剛好可解析的 JSON 會被寫進運勢資料表。

## 變更內容

1. 新增 `backend/services/claude_response.py`：依區塊 `type` 收集文字、讀 `stop_reason`；聊天類拒答回固定說明 `這個請求模型沒有回答，請換個說法再試一次。`、截斷照回並記警告；要解析的拒答或截斷丟 `ClaudeIncompleteResponse`。
2. `backend/services/claude_ai.py`：
   - 塔羅解讀：拒答時回 `None`，走原本的「AI 服務暫時無法使用」路徑，不存進 `ai_interpretation` 快取，同一筆抽牌可以再試；截斷照回並記警告。
   - 週運勢：改用 `complete_text`，拒答或截斷時丟錯，接到原本的 `except` 回 `None`，排程記為生成失敗。
3. `backend/routers/horoscope.py` 月運勢：改用 `complete_text`，拒答或截斷時不解析、不寫資料庫，回 `None`。
4. `backend/routers/tarot.py` 的 `/ai-test`（只在 DEBUG 開放）：改用聊天類的讀法。

## 影響範圍

- 只動上述檔案。模型 ID、max_tokens、提示詞、資料表、API 回應格式都不變。
- `requirements.txt` 已是 `anthropic==1.17.0`，不動。

## UI規格

無畫面變更。塔羅解讀遇到拒答時顯示原本的「AI 服務暫時無法使用」，重新整理可再試。

## 測試計畫

repo 沒有測試，用一次性腳本假造 SDK 回應（不打 API）呼叫四個呼叫點：

1. 第一塊 thinking、第二塊 text：四處都讀到 text，週運勢與月運勢解析成功。
2. `refusal`：塔羅回 `None`（有沒有文字都一樣），週運勢與月運勢回 `None` 且不寫資料庫，`/ai-test` 回固定說明。
3. `max_tokens`：塔羅照回並記一筆警告，週運勢與月運勢回 `None` 且不寫資料庫。
4. 上面幾項在改動前的程式要失敗。
