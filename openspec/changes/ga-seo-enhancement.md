---
title: Google Analytics 追蹤 + SEO 強化（中文市場）
type: feature
status: pending
priority: high
created: 2026-01-26
---

# Google Analytics 追蹤 + SEO 強化

## 目標

1. 加入 GA4 追蹤，監控流量來源與用戶行為
2. 強化 SEO，專注中文市場（宿曜道相關關鍵字）
3. 為未來多語系（日文版）做數據準備

---

## Phase 1：Google Analytics 4 整合

### 1.1 GA4 設定

```html
<!-- index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### 1.2 事件追蹤

| 事件名稱 | 觸發時機 | 參數 |
|---------|---------|------|
| `sukuyodo_lookup` | 查詢本命宿 | mansion_name |
| `sukuyodo_compatibility` | 計算相性 | relation_type, score |
| `horoscope_view` | 查看星座運勢 | zodiac_code, period |
| `tarot_draw` | 塔羅抽牌 | spread_type, card_count |
| `share_result` | 分享結果 | content_type |

### 1.3 Vue Router 整合

```typescript
// router/index.ts
router.afterEach((to) => {
  gtag('event', 'page_view', {
    page_title: to.meta.title,
    page_path: to.path
  })
})
```

---

## Phase 2：SEO Meta 優化

### 2.1 頁面 Meta 標籤

| 頁面 | Title | Description |
|------|-------|-------------|
| 首頁 | DashAstro - 星座運勢、塔羅占卜、宿曜道 | 免費星座運勢查詢、塔羅牌占卜、宿曜道本命宿分析。融合東西方占星智慧。 |
| 宿曜道 | 宿曜道 - 真言宗密教占星術｜本命宿查詢 | 源自印度、唐代傳入日本的密教占星術。輸入生日查詢你的本命宿與運勢。 |
| 相性診斷 | 宿曜道相性診斷 - 三九秘法｜雙人配對 | 使用三九秘法計算兩人的宿曜關係：命、業胎、栄親、友衰、安壊、危成。 |
| 星座運勢 | 12星座運勢 - 每日/週/月運勢查詢 | 牡羊座到雙魚座，每日更新的星座運勢、感情運、事業運。 |
| 塔羅占卜 | 線上塔羅占卜 - AI 解讀牌義 | 免費線上塔羅牌占卜，AI 即時解讀牌義，支援單牌、三牌、凱爾特十字牌陣。 |

### 2.2 關鍵字策略（中文市場）

**主要關鍵字**：
- 宿曜道、宿曜占星、本命宿
- 二十七宿、三九秘法
- 真言宗占星、密教占星
- 星座運勢、塔羅占卜

**長尾關鍵字**：
- 宿曜道配對、宿曜相性
- 本命宿查詢、農曆生日算命
- 免費星座運勢、今日運勢
- 線上塔羅牌占卜

### 2.3 Open Graph / Twitter Card

```html
<meta property="og:type" content="website">
<meta property="og:title" content="宿曜道 - 真言宗密教占星術">
<meta property="og:description" content="源自印度的密教占星術，查詢你的本命宿">
<meta property="og:image" content="https://astro.dashai.dev/og-sukuyodo.png">
<meta property="og:url" content="https://astro.dashai.dev/sukuyodo">

<meta name="twitter:card" content="summary_large_image">
```

---

## Phase 3：技術 SEO

### 3.1 Sitemap 自動生成

```xml
<!-- public/sitemap.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://astro.dashai.dev/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://astro.dashai.dev/sukuyodo</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://astro.dashai.dev/horoscope</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://astro.dashai.dev/tarot</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
```

### 3.2 robots.txt

```
User-agent: *
Allow: /
Sitemap: https://astro.dashai.dev/sitemap.xml
```

### 3.3 結構化資料 (Schema.org)

```json
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "DashAstro",
  "description": "星座運勢、塔羅占卜、宿曜道占星",
  "url": "https://astro.dashai.dev",
  "applicationCategory": "LifestyleApplication",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "TWD"
  }
}
```

### 3.4 FAQ Schema（宿曜道頁面）

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "什麼是宿曜道？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "宿曜道是源自印度的密教占星術，唐代由空海大師傳入日本..."
      }
    },
    {
      "@type": "Question",
      "name": "如何查詢本命宿？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "輸入你的西曆生日，系統會自動轉換為農曆並計算對應的二十七宿..."
      }
    }
  ]
}
```

---

## Phase 4：首頁宿曜道曝光

### 4.1 首頁卡片設計

```
┌─────────────────────────────────────┐
│  ☯ 宿曜道 - 密教占星術              │
│                                     │
│  源自印度、唐代傳入日本的占星智慧   │
│  查詢你的本命宿與命定關係           │
│                                     │
│  [查詢本命宿]  [相性診斷]           │
└─────────────────────────────────────┘
```

---

## 影響範圍

| 檔案 | 變更 |
|------|------|
| `frontend/index.html` | GA4 script、meta tags |
| `frontend/src/router/index.ts` | 頁面追蹤、meta 設定 |
| `frontend/src/views/HomeView.vue` | 宿曜道卡片 |
| `frontend/src/composables/useGtag.ts` | GA 事件封裝（新增）|
| `frontend/public/sitemap.xml` | Sitemap（新增）|
| `frontend/public/robots.txt` | Robots（新增）|
| `frontend/src/utils/seo.ts` | Schema.org 工具（新增）|

---

## 監控指標

| 指標 | 目標 | 監控方式 |
|------|------|---------|
| 自然搜尋流量 | 月增 20% | GA4 |
| 宿曜道頁面瀏覽 | 500+/月 | GA4 事件 |
| 搜尋引擎排名 | 「宿曜道」前 10 | Search Console |
| 日本 IP 佔比 | 觀察 | GA4 地區報告 |

---

## Checklist

### Phase 1（GA4）
- [ ] 建立 GA4 Property
- [ ] 加入追蹤碼到 index.html
- [ ] 實作 Vue Router 頁面追蹤
- [ ] 實作自訂事件追蹤

### Phase 2（Meta SEO）
- [ ] 各頁面加入 title/description
- [ ] 加入 Open Graph 標籤
- [ ] 加入 Twitter Card 標籤

### Phase 3（技術 SEO）
- [ ] 建立 sitemap.xml
- [ ] 建立 robots.txt
- [ ] 加入結構化資料
- [ ] 提交 Search Console

### Phase 4（首頁曝光）
- [ ] 首頁加入宿曜道卡片
- [ ] 卡片連結到宿曜道頁面

---

## 備註

- GA4 Property ID 需在 Vercel 環境變數設定
- 上線後提交 sitemap 到 Google Search Console
- 觀察 1-2 週流量數據再決定是否做日文版
