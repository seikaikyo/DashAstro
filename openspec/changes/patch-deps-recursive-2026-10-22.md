# 修補前端相依漏洞並鎖定後端 Python 相依

- **type**: fix
- **建立日期**: 2026-10-22

## 背景

2026-10-22 每日資安巡檢的 osv-scanner 原本沒有遞迴掃描子目錄，補上後重掃：

1. frontend/package-lock.json：9 個套件有已知漏洞。修補前 `npm audit`：moderate 4、high 9，共 13 筆（`--omit=dev` 為 high 5）。
2. backend/requirements.txt：全部用 `>=` 範圍，沒有任何釘版，每次部署都抓當下最新版。osv 依解析結果回報 certifi、httpx2、httpcore2 有已知漏洞。
3. 照目前範圍解析出的 SQLAlchemy 是 2.1.6。2.1 起不再自動安裝 greenlet，database.py 的 `sqlalchemy.ext.asyncio` 會在載入時丟 ImportError，下一次 Render 部署就會起不來。

## 變更內容

1. frontend：`npm update`，package.json 範圍不變，只改 lock 檔。
   - vue 與 @vue/* 3.5.27 → 3.5.44（含 @vue/server-renderer）
   - brace-expansion 2.0.2 → 2.1.7
   - minimatch 9.0.5 → 9.0.9
   - nanoid 3.3.11 → 3.3.20
   - postcss 8.5.6 → 8.5.31
   - rollup 4.56.0 → 4.64.6（4.65.0 在 2026-10-22 當天才發布，改用一週前的版本）
   - source-map-js 1.2.1 → 1.2.2
   - 連帶：@babel/parser 7.28.6 → 7.29.9、@types/estree 1.0.8 → 1.0.9 等同主版號修補版；rollup 4.64 起多一個 linux x64 專用的選用相依 @napi-rs/lzma-linux-x64-gnu
2. backend：原 requirements.txt 改名為 requirements.in，以 `uv pip compile --universal --python-version 3.11 --generate-hashes` 產生完整釘版、附雜湊值的 requirements.txt。Python 版本用 3.11，因為 backend/render.yaml 設定 `PYTHON_VERSION` 3.11.0；用 3.12 編出的 numpy 2.5.4 不支援 3.11。
3. requirements.in 補兩條約束：
   - `sqlalchemy[asyncio]`：把 greenlet 裝回來
   - `anthropic<2`：anthropic 2.0 在 2026-10-21 發布，先停在 1.17.0
4. 鎖定後 certifi 2026.10.19、httpx2 2.16.0、httpcore2 2.16.0，皆為已修補版。

## 影響範圍

| 對象 | 影響 |
| --- | --- |
| 執行期行為 | 前端只升修補版。後端鎖定的版本比 2026-05 上次部署時新（例如 fastapi 0.159.1、starlette 1.9.0、sqlalchemy 2.1.6、anthropic 1.17.0），跟不鎖版直接重新部署會裝到的版本相同，只是 anthropic 停在 1.x 並補回 greenlet。 |
| 依賴檔 | frontend/package-lock.json、backend/requirements.in、backend/requirements.txt。 |
| 部署 | Vercel 與 Render 依 git push 自動部署；Render 建構指令維持 `pip install -r requirements.txt`。 |

## 剩餘風險

1. 前端修補後 `npm audit`：moderate 4、high 1，共 5 筆，全部是開發期工具：vite 5.4.21 與 esbuild 0.21.5 要升到 vite 6 才修得掉；vue-template-compiler 由 vue-tsc 1.x 引入，沒有修補版，要升 vue-tsc 2 以上才會移除。`--omit=dev` 修補後 0 筆。
2. 後端冒煙測試只涵蓋載入與 `/health`，Claude 解讀與資料庫路徑要部署後實際打一次。

## UI 規格

無 UI 變更。

## 測試計畫

1. frontend：`npm ci` 後 `npm run build` 修補前後都成功；`npm run type-check` 修補前後都是相同的 23 個既有型別錯誤。
2. backend：Python 3.11 與 3.12 虛擬環境都以 `--require-hashes` 安裝成功；載入 `main`、`/health` 回 200、anthropic 用戶端與 SQLAlchemy async engine 可建立。
3. 推送後確認 Vercel 與 Render 部署成功，打一次塔羅解讀與宿曜道 API，並重跑每日巡檢確認漏洞數下降。
