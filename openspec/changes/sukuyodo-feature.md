---
title: 宿曜道（Sukuyodo）東洋占星功能
type: feature
status: in-progress
created: 2026-01-25
---

# 宿曜道（Sukuyodo）東洋占星功能

## 變更內容

新增日本真言宗宿曜道占星功能，基於空海從中國帶回的《宿曜經》，提供：
1. 依據農曆生日計算用戶的「本命宿」（27宿之一）
2. 本命宿的性格分析（白話易懂版本）
3. 雙人相性診斷（六種關係 + 距離影響）
4. 與現有星座功能整合，提供東西方雙重視角

## 背景說明

宿曜道是日本真言宗密教使用的占星系統，有 1200+ 年歷史：
- 803 年由空海從中國帶回日本
- 基於月亮 27.3 天軌道週期
- 平安時代與陰陽師齊名
- 德川家康據說用此分析諸侯相性

## 影響範圍

### 後端新增
| 檔案 | 說明 |
|------|------|
| `backend/models/sukuyodo.py` | 宿曜資料模型 |
| `backend/services/sukuyodo.py` | 計算服務（農曆轉換 + 27宿計算 + 相性） |
| `backend/routers/sukuyodo.py` | API 路由 |
| `backend/data/sukuyodo_mansions.json` | 27宿資料（名稱、性格、關鍵字） |

### 前端新增
| 檔案 | 說明 |
|------|------|
| `frontend/src/views/SukuyodoView.vue` | 宿曜主頁面 |
| `frontend/src/components/sukuyodo/MansionCard.vue` | 宿星卡片元件 |
| `frontend/src/components/sukuyodo/CompatibilityResult.vue` | 相性結果元件 |

### 資料庫
| 資料表 | 說明 |
|--------|------|
| `sukuyodo_mansions` | 27宿基本資料 |
| `sukuyodo_readings` | 用戶查詢紀錄（統計用） |

## 技術規格

### 計算邏輯

**Step 1: 西曆 → 農曆轉換**
使用 `lunarcalendar` 或 `chinese-calendar` Python 套件

**Step 2: 農曆 → 本命宿**
月宿傍通曆對照：
```python
MONTH_START_MANSION = {
    1: 11,   # 室宿 (index 11)
    2: 13,   # 奎宿 (index 13)
    3: 15,   # 胃宿 (index 15)
    4: 17,   # 畢宿 (index 17)
    5: 19,   # 參宿 (index 19)
    6: 21,   # 鬼宿 (index 21)
    7: 24,   # 張宿 (index 24)
    8: 0,    # 角宿 (index 0)
    9: 2,    # 氐宿 (index 2)
    10: 4,   # 心宿 (index 4)
    11: 7,   # 斗宿 (index 7)
    12: 9,   # 虛宿 (index 9)
}

def get_mansion(lunar_month: int, lunar_day: int) -> int:
    start = MONTH_START_MANSION[lunar_month]
    return (start + lunar_day - 1) % 27
```

**Step 3: 相性計算（三九秘法）**
```python
def get_relationship(mansion1: int, mansion2: int) -> dict:
    diff = (mansion2 - mansion1) % 27
    # 命: diff == 0
    # 業: diff == 9
    # 胎: diff == 18
    # 其他依據 diff 對應到 栄親/友衰/安壊/危成
```

### API 設計

```
GET  /api/sukuyodo/mansion/{birth_date}     # 查詢本命宿
GET  /api/sukuyodo/mansions                 # 27宿列表
POST /api/sukuyodo/compatibility            # 雙人相性
```

### 27宿資料結構

```json
{
  "index": 0,
  "name_jp": "角宿",
  "name_zh": "角宿",
  "reading": "かくしゅく",
  "element": "木",
  "personality": "獨立自主，有領導氣質...",
  "keywords": ["領導", "獨立", "開創"],
  "love": "感情上比較主動...",
  "career": "適合開創性工作...",
  "health": "注意頭部和肝膽..."
}
```

### 相性關係說明（白話版）

| 關係 | 白話解釋 |
|------|---------|
| 命 | 遇到跟你一樣的人了！想法超合拍，但也可能互相看不順眼 |
| 業胎 | 上輩子就認識的感覺，不用多說就懂對方在想什麼 |
| 栄親 | 最佳拍檔！在一起會互相變更好，結婚首選 |
| 友衰 | 相處很舒服，但容易一起耍廢，要小心變成損友 |
| 安壊 | 超有吸引力但危險！可能是渣男/渣女體質，請小心 |
| 危成 | 個性差很多，但能互補。願意磨合的話會是好組合 |

## UI/UX 規格

### 配色
沿用現有星語紫金設計系統，新增：
- 宿曜專屬漸層：`--sukuyodo-gradient: linear-gradient(135deg, #2A2438, #1A1625)`
- 月亮意象：使用銀白色 `--moon-silver: #B8C4D0`

### 頁面結構
1. **輸入區**：生日選擇器（預設帶入用戶設定的生日）
2. **結果區**：本命宿卡片（名稱、性格、關鍵字）
3. **詳細說明**：展開式內容（感情/事業/健康）
4. **相性功能**：可輸入另一人生日進行比對

### 互動
- 宿星卡片 hover 時有月光光暈效果
- 相性結果以視覺化圓盤呈現 27 宿位置

## 測試計畫

1. **農曆轉換驗證**
   - 用線上工具（香港天文台）對照 10+ 個日期
   - 邊界測試：閏月、月底

2. **本命宿計算驗證**
   - 用 [八雲院](https://yakumoin.net/) 對照 10+ 個生日
   - 確認計算結果一致

3. **相性計算驗證**
   - 確認三九秘法計算正確
   - 測試所有 6 種關係 + 3 種距離

4. **前端測試**
   - 頁面載入無錯誤
   - RWD 手機/平板/桌面
   - 文字可讀性（白話夠不夠白話）

## Checklist

### Phase 1: 後端基礎
- [ ] 建立 `sukuyodo.py` 資料模型
- [ ] 實作農曆轉換服務
- [ ] 實作 27 宿計算邏輯
- [ ] 建立 27 宿 JSON 資料檔
- [ ] 建立 API 路由
- [ ] 驗證計算準確性

### Phase 2: 前端實作
- [ ] 建立 SukuyodoView.vue 頁面
- [ ] 實作 MansionCard 元件
- [ ] 實作相性功能
- [ ] 整合到導航列

### Phase 3: 資料完善
- [ ] 撰寫 27 宿白話性格描述
- [ ] 撰寫相性關係詳細說明
- [ ] 新增使用統計追蹤

## 參考資料

- [宿曜占星術 八雲院](https://yakumoin.net/)
- [月宿傍通曆](https://www.divination.page/2024/03/honmeisyuku.html)
- [宿曜相性解說](https://uranai.blog/shukuyo-aisho/)
