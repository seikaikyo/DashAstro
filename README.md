# DashAstro 占星工具平台

融合日本密教占星 (宿曜道)、西方現代占星、日本傳統曆法的專業占星平台。

## 功能

### 宿曜道 (日本密教占星)
- **27 宿本命宿**: 西曆 → 農曆 → 月宿傍通曆精確計算
- **三九秘法相性**: 6 種關係 (栄親/友衰/安壊/危成/命/業胎) + 五行加成
- **多維度運勢**: 日運/月運/週運、三期週期、暗黑週間、凌犯逆轉

### 西方占星
- **12 星座運勢**: 週運 + 月運 (Claude AI 生成)
- **行星位置**: Skyfield 計算 10 大行星黃經、星座度數、逆行狀態
- **相位分析**: 合/六分/四分/三分/對分 (容許度 6-8 度)
- **星座相性**: 元素相容性 + 相位距離計算

### 塔羅牌占卜
- **22 張大阿爾克那**: 正位/逆位完整牌義
- **多牌陣**: 單牌、三牌、凱爾特十字 (10 牌)
- **Claude AI 解讀**: 自然語言風格解牌

### 日本吉日曆
- **六曜 + 干支 + 一粒萬倍日**
- **多類型查詢**: 婚禮、搬家、開業、美容、感情、購物

## 技術棧

| 層級 | 技術 |
|------|------|
| 前端 | Vue 3 + TypeScript + Shoelace + Vue Router + Pinia |
| 後端 | FastAPI + SQLModel + Neon PostgreSQL |
| 星曆計算 | Skyfield (NASA JPL 星曆) |
| 農曆轉換 | lunarcalendar |
| AI | Claude API (運勢生成 + 塔羅解讀) |
| 部署 | Vercel (前端) + Render (後端) |

## API (9 個路由群組)

| 路由 | 功能 |
|------|------|
| `/api/sukuyodo/*` | 27 宿查詢、本命宿、雙人相性 |
| `/api/horoscope/*` | 12 星座週運/月運 |
| `/api/tarot/*` | 抽牌、AI 解讀 |
| `/api/astronomy/*` | 行星位置、相位、月相、逆行 |
| `/api/compatibility/*` | 星座相性分析 |
| `/api/lucky-days/*` | 吉日查詢 (日/月/區間) |

## 開發

```bash
# 前端 (port 5171)
cd frontend && npm install && npm run dev

# 後端 (port 8001)
cd backend && source venv/bin/activate && uvicorn main:app --port 8001
```
