# DashAstro

## 專案概述

占星綜合平台 — 宿曜道 27 宿 + 西洋 12 星座 + 塔羅牌 + 日本曆注。
獨立部署（不走 dashai-api gateway）。

## 技術架構

| 層 | 技術 |
|-----|------|
| 前端 | Vue 3.4 + TypeScript 5.3 + Vite 5 |
| UI | Shoelace（非 PrimeVue，歷史因素） |
| 狀態 | Composables + localStorage（無 Pinia） |
| 後端 | FastAPI + SQLModel |
| 天文 | Skyfield (NASA JPL 星曆表) |
| 農曆 | lunarcalendar |
| AI | Anthropic Claude (claude-sonnet-4-20250514) |
| DB | Neon PostgreSQL (Singapore) + psycopg + asyncpg |
| 部署 | Vercel (前端) + Render (後端, Singapore, Free) |
| Python | 3.11.0 (render.yaml) |

## 前端結構

```
frontend/src/
├── views/          # 9 個路由頁面
├── components/     # 13 元件（含 sukuyodo 子目錄）
├── stores/         # localStorage profile 狀態
├── composables/    # useGtag, useSukuyodo
├── router/         # Vue Router 設定
├── config/         # API 設定
├── styles/         # global.css, variables.css
└── App.vue, main.ts
```

### 前端路由（9 個）

| 路徑 | 功能 |
|------|------|
| `/` | 首頁 |
| `/horoscope`, `/horoscope/:code` | 星座運勢 |
| `/tarot`, `/tarot/reading/:id` | 塔羅占卜 |
| `/sky` | 即時星空 |
| `/profile` | 個人資料 |
| `/stats` | 使用統計 |
| `/sukuyodo`, `/sukuyodo-legacy` | 宿曜道（新舊版） |

## 後端結構

```
backend/
├── routers/        # 9 個 API router
├── models/         # SQLModel 定義
├── services/       # 業務邏輯（astrology, claude_ai, compatibility 等）
├── data/           # 靜態資料
├── main.py         # FastAPI 入口
├── config.py       # Settings, Claude model
├── database.py     # SQLModel + Neon PostgreSQL
└── requirements.txt
```

### 後端路由（9 組）

| 路由 | 功能 |
|------|------|
| `/health` | 健康檢查 |
| `/api/sukuyodo/*` | 27 宿計算、相性 |
| `/api/horoscope/*` | 12 星座週/月運 |
| `/api/tarot/*` | 塔羅抽牌 + AI 解讀 |
| `/api/astronomy/*` | 行星位置、月相 |
| `/api/compatibility/*` | 星座相性 |
| `/api/lucky-days/*` | 日本曆注（六曜/干支） |
| `/api/stats/*` | 使用統計 |
| `/api/cron/*` | 排程任務 |

## CORS 設定

- `localhost:5173`, `localhost:3000`
- `https://astro.dashai.dev`
- `https://dashastro.vercel.app`（含 preview domains）

## 開發注意事項

- Skyfield 需下載 JPL 星曆檔（de421.bsp），首次啟動慢
- 前端用 Shoelace 不是 PrimeVue（歷史因素，`sl-*` custom elements）
- 獨立 Render instance，不是 dashai-api 子模組
- requirements.txt 必須鎖版本
- sukuyodo.py 是最大的 service（~70KB），修改需謹慎
