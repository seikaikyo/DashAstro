---
title: 宿曜道付費功能規劃
type: feature
status: pending
trigger: usage-based
created: 2025-01-25
---

# 宿曜道付費功能規劃

## 觸發條件

當以下任一條件達成時，啟動此規劃：

| 指標 | 門檻 | 監控方式 |
|------|------|---------|
| 宿曜道月使用次數 | >= 500 次 | usage_stats 表 |
| 相性診斷月使用次數 | >= 200 次 | usage_stats 表 |
| 用戶主動詢問付費 | >= 3 人 | 人工記錄 |

監控 SQL：
```sql
SELECT feature, SUM(count) as total
FROM usage_stats
WHERE feature IN ('sukuyodo_lookup', 'sukuyodo_compat')
  AND stat_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY feature;
```

---

## Phase A：東西並行（低調期）

**目標**：維持現狀，宿曜道作為隱藏功能

### 現有狀態
- [x] 27 宿本命宿查詢
- [x] 雙人相性診斷（三九秘法）
- [x] 導航列入口
- [x] 使用統計追蹤

### 待優化項目（觸發前可做）
- [ ] 首頁加入宿曜道卡片（低調露出）
- [ ] SEO 優化（宿曜道相關關鍵字）
- [ ] 分享功能（本命宿結果可分享）

---

## Phase B：雙軌付費（觸發後實作）

**目標**：西洋免費、東方進階付費

### B1. 會員系統

**技術選型**：
| 選項 | 優點 | 缺點 |
|------|------|------|
| Clerk | 快速整合、免費額度高 | 依賴第三方 |
| Supabase Auth | 自主性高、與 Neon 相容 | 需自建 UI |
| 自建 JWT | 完全掌控 | 開發時間長 |

**建議**：Clerk（快速上線）→ 未來視需求遷移

**會員等級**：
| 等級 | 價格 | 權限 |
|------|------|------|
| 免費 | $0 | 基本宿位查詢、簡易相性 |
| 月費 | NT$99/月 | 完整報告、流年運勢、PDF 下載 |
| 年費 | NT$799/年 | 同上 + 優先功能 |
| 單次 | NT$49/次 | 單份完整報告 |

### B2. 付費功能內容

**免費版（現有功能）**：
- 本命宿名稱 + 元素 + 關鍵字
- 基本性格描述
- 相性關係類型 + 分數

**付費版（新增）**：
- 完整性格深度分析（2000+ 字）
- 感情/事業/健康詳細運勢
- 流年運勢（今年、明年）
- 雙人相性完整報告
  - 相處建議（具體情境）
  - 潛在衝突點與化解方法
  - 適合共同發展的方向
- PDF 報告下載
- 歷史記錄保存

### B3. 資料庫變更

```sql
-- 會員表
CREATE TABLE members (
  id SERIAL PRIMARY KEY,
  clerk_id VARCHAR(255) UNIQUE,
  email VARCHAR(255),
  plan VARCHAR(20) DEFAULT 'free',  -- free, monthly, yearly
  plan_expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 付費報告表
CREATE TABLE sukuyodo_reports (
  id SERIAL PRIMARY KEY,
  member_id INT REFERENCES members(id),
  report_type VARCHAR(20),  -- mansion, compatibility
  birth_date DATE,
  partner_date DATE,
  report_data JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 交易記錄
CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  member_id INT REFERENCES members(id),
  amount INT,
  currency VARCHAR(3) DEFAULT 'TWD',
  product VARCHAR(50),
  status VARCHAR(20),
  provider VARCHAR(20),  -- stripe, ecpay
  provider_id VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### B4. 金流整合

**建議**：綠界 ECPay（台灣在地、手續費低）

| 方式 | 手續費 | 適合 |
|------|--------|------|
| 信用卡 | 2.75% | 月費/年費 |
| ATM | $15/筆 | 單次購買 |
| 超商代碼 | $25/筆 | 無信用卡用戶 |

---

## Phase C：阿闍梨品牌（長期願景）

**條件**：Phase B 穩定運營 + 用戶正向回饋

### 品牌升級
- 「真言宗傳承者監修」標章
- 阿闍梨專欄（每月運勢解說）
- 高端服務：一對一諮詢（預約制）

### 定價參考
| 服務 | 價格 | 說明 |
|------|------|------|
| 線上諮詢 30 分鐘 | NT$1,500 | 視訊解讀 |
| 完整命盤分析 | NT$3,000 | 書面報告 + 語音解說 |
| 合婚/合夥診斷 | NT$5,000 | 雙人深度分析 |

---

## 影響範圍

### Phase B 需修改的檔案
| 檔案 | 變更 |
|------|------|
| `backend/models/member.py` | 新增會員模型 |
| `backend/routers/auth.py` | Clerk 整合 |
| `backend/routers/sukuyodo.py` | 加入權限檢查 |
| `backend/services/sukuyodo.py` | 擴充報告內容 |
| `frontend/src/stores/auth.ts` | 會員狀態管理 |
| `frontend/src/views/SukuyodoView.vue` | 付費牆 UI |
| `frontend/src/views/PricingView.vue` | 定價頁（新增）|

---

## Checklist

### 觸發前（可隨時做）
- [ ] 監控使用數據
- [ ] 收集用戶回饋
- [ ] 準備付費版文案（27 宿完整分析）

### 觸發後（Phase B）
- [ ] 會員系統整合
- [ ] 金流串接
- [ ] 付費功能開發
- [ ] 定價頁設計
- [ ] 隱私權政策更新

---

## 自動監控設定

### 已實作
- `backend/services/milestone_monitor.py` - 監控服務
- `backend/routers/cron.py` - Cron API 端點
- `POST /api/cron/milestone-check` - 每日檢查端點

### Render Cron Job 設定步驟

1. 進入 Render Dashboard → DashAstro API 服務
2. 點選 "Cron Jobs" → "New Cron Job"
3. 設定：
   ```
   Name: milestone-check
   Command: curl -X POST https://dashastro-api.onrender.com/api/cron/milestone-check -H "X-Cron-Secret: $CRON_SECRET"
   Schedule: 0 9 * * * (每天早上 9 點)
   ```

4. 環境變數設定：
   ```
   CRON_SECRET=<自訂密鑰>
   LINE_NOTIFY_TOKEN=<LINE Notify Token>
   ```

### LINE Notify 設定
1. 前往 https://notify-bot.line.me/
2. 登入 → 發行權杖
3. 選擇要通知的聊天室（1:1 或群組）
4. 複製 Token 設定到環境變數

### 通知規則
- 每週一固定發送週報
- 任何里程碑達標時立即通知

---

## 金流整合

### 建議方案：paid.tw Skill
- GitHub: https://github.com/paid-tw/skills
- 台灣在地金流，整合簡單
- 支援：信用卡、ATM、超商代碼

### 整合時機
觸發 Phase B 後再安裝：
```bash
# 安裝 paid.tw skill
mkdir -p ~/.claude/skills/paid-tw
curl -o ~/.claude/skills/paid-tw/SKILL.md \
  https://raw.githubusercontent.com/paid-tw/skills/main/SKILL.md
```

---

## 備註

- 阿闍梨身份揭露與否由本人決定
- 宗教相關內容需謹慎措辭，避免爭議
- 付費功能上線前需測試金流完整性
