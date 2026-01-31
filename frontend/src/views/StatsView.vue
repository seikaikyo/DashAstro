<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { apiUrl } from '@/config/api'

interface StatsSummary {
  period_days: number
  period_start: string
  period_end: string
  total_usage: number
  by_feature: Record<string, number>
  today: {
    total: number
    by_feature: Record<string, number>
  }
}

interface DailyData {
  feature: string
  date: string
  count: number
}

interface FeatureInfo {
  code: string
  name: string
}

const summary = ref<StatsSummary | null>(null)
const dailyData = ref<DailyData[]>([])
const features = ref<FeatureInfo[]>([])
const loading = ref(true)
const selectedDays = ref(7)

const featureNameMap = computed(() => {
  const map: Record<string, string> = {}
  for (const f of features.value) {
    map[f.code] = f.name
  }
  return map
})

// 計算每日總計
const dailyTotals = computed(() => {
  const totals: Record<string, number> = {}
  for (const d of dailyData.value) {
    if (!totals[d.date]) totals[d.date] = 0
    totals[d.date] += d.count
  }
  // 轉為排序後的陣列
  return Object.entries(totals)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([date, count]) => ({ date, count }))
})

// 最高使用功能
const topFeature = computed(() => {
  if (!summary.value || Object.keys(summary.value.by_feature).length === 0) return null
  const entries = Object.entries(summary.value.by_feature)
  entries.sort((a, b) => b[1] - a[1])
  const [code, count] = entries[0]
  return { code, name: featureNameMap.value[code] || code, count }
})

onMounted(async () => {
  try {
    const [summaryRes, dailyRes, featuresRes] = await Promise.all([
      fetch(`${apiUrl}/api/stats/summary?days=${selectedDays.value}`),
      fetch(`${apiUrl}/api/stats/daily?days=${selectedDays.value}`),
      fetch(`${apiUrl}/api/stats/features`)
    ])

    if (summaryRes.ok) summary.value = await summaryRes.json()
    if (dailyRes.ok) {
      const data = await dailyRes.json()
      dailyData.value = data.data || []
    }
    if (featuresRes.ok) {
      const data = await featuresRes.json()
      features.value = data.features || []
    }
  } catch (e) {
    console.error('載入統計失敗', e)
  } finally {
    loading.value = false
  }
})

async function changeDays(days: number) {
  selectedDays.value = days
  loading.value = true
  try {
    const [summaryRes, dailyRes] = await Promise.all([
      fetch(`${apiUrl}/api/stats/summary?days=${days}`),
      fetch(`${apiUrl}/api/stats/daily?days=${days}`)
    ])

    if (summaryRes.ok) summary.value = await summaryRes.json()
    if (dailyRes.ok) {
      const data = await dailyRes.json()
      dailyData.value = data.data || []
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<template>
  <div class="stats-page">
    <div class="container">
      <header class="page-header">
        <h1>使用統計</h1>
        <p class="subtitle">追蹤網站功能使用情況</p>
      </header>

      <div v-if="loading" class="loading">
        <sl-spinner style="font-size: 2rem;"></sl-spinner>
      </div>

      <template v-else-if="summary">
        <!-- 時間範圍選擇 -->
        <div class="period-selector">
          <button
            v-for="days in [7, 14, 30]"
            :key="days"
            :class="['period-btn', { active: selectedDays === days }]"
            @click="changeDays(days)"
          >
            {{ days }} 天
          </button>
        </div>

        <!-- 摘要卡片 -->
        <div class="summary-cards">
          <div class="stat-card">
            <div class="stat-value">{{ summary.total_usage }}</div>
            <div class="stat-label">總使用次數</div>
            <div class="stat-period">過去 {{ selectedDays }} 天</div>
          </div>

          <div class="stat-card highlight">
            <div class="stat-value">{{ summary.today.total }}</div>
            <div class="stat-label">今日使用</div>
          </div>

          <div v-if="topFeature" class="stat-card">
            <div class="stat-value">{{ topFeature.name }}</div>
            <div class="stat-label">最熱門功能</div>
            <div class="stat-period">{{ topFeature.count }} 次</div>
          </div>
        </div>

        <!-- 功能明細 -->
        <section class="section card">
          <h2>功能使用明細</h2>
          <div class="feature-list">
            <div
              v-for="feature in features"
              :key="feature.code"
              class="feature-row"
            >
              <span class="feature-name">{{ feature.name }}</span>
              <div class="feature-bar-container">
                <div
                  class="feature-bar"
                  :style="{
                    width: summary.total_usage > 0
                      ? `${((summary.by_feature[feature.code] || 0) / summary.total_usage) * 100}%`
                      : '0%'
                  }"
                ></div>
              </div>
              <span class="feature-count">{{ summary.by_feature[feature.code] || 0 }}</span>
            </div>
          </div>
        </section>

        <!-- 每日趨勢 -->
        <section class="section card">
          <h2>每日趨勢</h2>
          <div class="daily-chart">
            <div
              v-for="day in dailyTotals"
              :key="day.date"
              class="chart-bar-wrapper"
            >
              <div class="chart-bar-container">
                <div
                  class="chart-bar"
                  :style="{
                    height: dailyTotals.length > 0 && Math.max(...dailyTotals.map(d => d.count)) > 0
                      ? `${(day.count / Math.max(...dailyTotals.map(d => d.count))) * 100}%`
                      : '0%'
                  }"
                ></div>
              </div>
              <div class="chart-label">{{ formatDate(day.date) }}</div>
              <div class="chart-value">{{ day.count }}</div>
            </div>
          </div>
        </section>

        <!-- 今日明細 -->
        <section v-if="summary.today.total > 0" class="section card">
          <h2>今日使用明細</h2>
          <div class="today-list">
            <div
              v-for="(count, code) in summary.today.by_feature"
              :key="code"
              class="today-item"
            >
              <span class="today-name">{{ featureNameMap[code] || code }}</span>
              <span class="today-count">{{ count }} 次</span>
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<style scoped>
.stats-page {
  padding: var(--space-6) 0;
}

.page-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.page-header h1 {
  margin-bottom: var(--space-2);
}

.subtitle {
  color: var(--text-muted);
}

.loading {
  text-align: center;
  padding: var(--space-12);
}

/* 時間選擇器 */
.period-selector {
  display: flex;
  justify-content: center;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
}

.period-btn {
  padding: var(--space-2) var(--space-4);
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.period-btn:hover {
  border-color: var(--stellar-gold);
  color: var(--stellar-gold);
}

.period-btn.active {
  background: var(--stellar-gold);
  border-color: var(--stellar-gold);
  color: var(--cosmos-night);
}

/* 摘要卡片 */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--cosmos-dusk);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  text-align: center;
}

.stat-card.highlight {
  border-color: var(--stellar-gold);
  background: linear-gradient(135deg, var(--cosmos-dusk), var(--astral-deep));
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: var(--stellar-gold);
  margin-bottom: var(--space-1);
}

.stat-label {
  color: var(--text-primary);
  font-weight: 500;
}

.stat-period {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-top: var(--space-1);
}

/* 區塊 */
.section {
  margin-bottom: var(--space-6);
}

.section h2 {
  color: var(--stellar-gold);
  margin-bottom: var(--space-4);
  font-size: 1.1rem;
}

/* 功能列表 */
.feature-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.feature-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.feature-name {
  width: 100px;
  flex-shrink: 0;
  color: var(--text-secondary);
}

.feature-bar-container {
  flex: 1;
  height: 8px;
  background: var(--cosmos-twilight);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.feature-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--astral-medium), var(--stellar-gold));
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.feature-count {
  width: 50px;
  text-align: right;
  color: var(--text-primary);
  font-weight: 500;
}

/* 每日趨勢圖 */
.daily-chart {
  display: flex;
  align-items: flex-end;
  gap: var(--space-2);
  height: 150px;
  padding-top: var(--space-4);
}

.chart-bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.chart-bar-container {
  flex: 1;
  width: 100%;
  max-width: 40px;
  display: flex;
  align-items: flex-end;
}

.chart-bar {
  width: 100%;
  background: linear-gradient(180deg, var(--stellar-gold), var(--astral-medium));
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  min-height: 4px;
  transition: height 0.3s ease;
}

.chart-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: var(--space-2);
}

.chart-value {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* 今日明細 */
.today-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.today-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.today-name {
  color: var(--text-secondary);
}

.today-count {
  color: var(--stellar-gold);
  font-weight: 500;
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }

  .daily-chart {
    overflow-x: auto;
    padding-bottom: var(--space-2);
  }

  .chart-bar-wrapper {
    min-width: 40px;
  }
}
</style>
