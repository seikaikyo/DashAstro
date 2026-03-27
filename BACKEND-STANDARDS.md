# DashAstro 後端開發規範

> 修改後端程式碼前必須先讀此文件。

---

## 1. API 路由設計

### 1.1 URL 命名
```
/api/{resource}          # 資源列表
/api/{resource}/{id}     # 單一資源
```

| 規則 | 範例 |
|------|------|
| 資源名用複數小寫 | `/api/horoscope`, `/api/tarot` |
| 用連字號分隔 | `/api/lucky-days` |
| 動作用 HTTP method 表達 | POST 建立, PATCH 更新 |

---

## 2. 回應格式（強制）

### 2.1 統一信封
```python
# 成功（單一資源）
{"success": True, "data": {...}}

# 成功（列表 + 分頁）
{"success": True, "data": [...], "total": 42, "page": 1, "limit": 20}

# 錯誤
{"success": False, "error": "具體錯誤訊息"}
```

### 2.2 HTTP 狀態碼
| 碼 | 用途 |
|----|------|
| 200 | 成功 |
| 400 | 請求格式錯誤 |
| 404 | 資源不存在 |
| 429 | Rate limit |
| 500 | 伺服器錯誤 |
| 503 | 服務不可用（禁止回 mock data） |

---

## 3. 資料庫規範

### 3.1 連線
- Neon PostgreSQL (aws-ap-southeast-1)
- psycopg + asyncpg
- Pool: `pool_size=5, max_overflow=5, pool_timeout=10, pool_recycle=300, pool_pre_ping=True`

### 3.2 Model 定義
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class MyModel(SQLModel, table=True):
    __tablename__ = "my_models"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.3 禁止事項
- asyncpg 不接受 aware datetime，用 `datetime.utcnow()`（naive）
- asyncpg 不接受字串日期，用 `date.fromisoformat()` 轉 date 物件
- 改欄位名必須手動 `ALTER TABLE RENAME COLUMN`

---

## 4. 錯誤處理

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="Resource not found")
raise HTTPException(status_code=503, detail="Claude API unavailable")
```

- 禁止 bare `except:` 吞錯誤
- 禁止回 mock/fallback data 取代 503

---

## 5. LLM 整合

- AI model: `claude-sonnet-4-20250514`（config.py）
- 用 `config.py` 的 Settings 取 API key，禁止直接讀 `os.environ`
- 所有 AI 呼叫必須有 error handling + timeout

---

## 6. 安全規範

### 6.1 CORS
- 白名單: localhost, astro.dashai.dev, dashastro.vercel.app
- 新增前端域名需更新 CORS 列表

### 6.2 禁止
- 禁止 log 機敏資料（API key, token）
- 禁止 `print()` 做日誌，用 `logging.getLogger(__name__)`

---

## 7. 健康檢查

- `/health` endpoint（UptimeRobot 每 5 分鐘 ping）
- Render Free 方案有冷啟動

---

## 8. 部署

- `git push` 自動觸發 Render 部署
- Python 3.11.0（render.yaml 鎖定）
- requirements.txt 必須鎖版本
- 推送前 `python -m py_compile main.py` + 本機啟動測試

---

## 9. 測試

```bash
# 語法檢查
python -m py_compile main.py

# 本機啟動
uvicorn main:app --port 8008

# API 測試
curl http://localhost:8008/health
curl http://localhost:8008/api/sukuyodo/mansions
```

- 禁止 py_compile 通過就推送，必須實際啟動測試
