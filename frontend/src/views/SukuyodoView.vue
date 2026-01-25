<script setup lang="ts">
import { ref, computed } from 'vue'

interface Mansion {
  index: number
  name_jp: string
  name_zh: string
  reading: string
  element: string
  personality: string
  keywords: string[]
  love: string
  career: string
  health: string
  lunar_date?: {
    year: number
    month: number
    day: number
    display: string
  }
}

interface Relation {
  type: string
  name: string
  name_jp: string
  description: string
  advice: string
}

interface CompatibilityResult {
  person1: {
    date: string
    mansion: string
    reading: string
    element: string
    keywords: string[]
  }
  person2: {
    date: string
    mansion: string
    reading: string
    element: string
    keywords: string[]
  }
  relation: Relation
  score: number
  summary: string
}

const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'

// 本命宿查詢
const birthDate = ref('')
const mansion = ref<Mansion | null>(null)
const lookupLoading = ref(false)
const lookupError = ref('')
const showDetails = ref(false)

// 相性診斷
const date1 = ref('')
const date2 = ref('')
const compatibility = ref<CompatibilityResult | null>(null)
const compatLoading = ref(false)
const compatError = ref('')

// 元素顏色
const elementColors: Record<string, string> = {
  '木': '#4A9B5A',
  '金': '#C4A052',
  '土': '#8B7355',
  '日': '#E89B3C',
  '月': '#7CB3D9',
  '火': '#E85D4C',
  '水': '#5B8FA8'
}

const mansionElementColor = computed(() => {
  return mansion.value ? elementColors[mansion.value.element] : ''
})

const lookupMansion = async () => {
  if (!birthDate.value) return

  lookupLoading.value = true
  lookupError.value = ''
  mansion.value = null
  showDetails.value = false

  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/mansion/${birthDate.value}`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        mansion.value = data.data
      } else {
        lookupError.value = data.error || '查詢失敗'
      }
    } else {
      const err = await res.json()
      lookupError.value = err.detail || '查詢失敗'
    }
  } catch (e) {
    lookupError.value = '無法連線到伺服器'
  } finally {
    lookupLoading.value = false
  }
}

const calculateCompatibility = async () => {
  if (!date1.value || !date2.value) return

  compatLoading.value = true
  compatError.value = ''
  compatibility.value = null

  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/compatibility`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        date1: date1.value,
        date2: date2.value
      })
    })
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        compatibility.value = data.data
      } else {
        compatError.value = data.error || '分析失敗'
      }
    } else {
      const err = await res.json()
      compatError.value = err.detail || '分析失敗'
    }
  } catch (e) {
    compatError.value = '無法連線到伺服器'
  } finally {
    compatLoading.value = false
  }
}

const getScoreLevel = (score: number) => {
  if (score >= 90) return { text: '天作之合', class: 'excellent' }
  if (score >= 75) return { text: '相當不錯', class: 'good' }
  if (score >= 60) return { text: '需要磨合', class: 'fair' }
  return { text: '多加小心', class: 'warning' }
}
</script>

<template>
  <div class="sukuyodo-page">
    <div class="container">
      <header class="page-header">
        <h1>宿曜道</h1>
        <p>日本真言宗占星術 - 依農曆生日揭示你的本命宿星</p>
      </header>

      <!-- 本命宿查詢 -->
      <section class="lookup-section card card-gold">
        <h2 class="section-title">查詢本命宿</h2>
        <p class="section-desc">輸入你的西曆生日，系統會自動轉換為農曆並計算你的本命宿</p>

        <div class="form-row">
          <sl-input
            type="date"
            v-model="birthDate"
            label="西曆生日"
            :max="new Date().toISOString().split('T')[0]"
          ></sl-input>
          <button
            class="btn-gold"
            @click="lookupMansion"
            :disabled="!birthDate || lookupLoading"
          >
            <sl-spinner v-if="lookupLoading"></sl-spinner>
            <span v-else>查詢</span>
          </button>
        </div>

        <div v-if="lookupError" class="error-msg">
          {{ lookupError }}
        </div>

        <!-- 本命宿結果 -->
        <div v-if="mansion" class="mansion-result">
          <div class="mansion-header" :style="{ '--element-color': mansionElementColor }">
            <div class="mansion-name-group">
              <span class="mansion-name">{{ mansion.name_jp }}</span>
              <span class="mansion-reading">{{ mansion.reading }}</span>
            </div>
            <span class="mansion-element">{{ mansion.element }}</span>
          </div>

          <div v-if="mansion.lunar_date" class="lunar-date">
            {{ mansion.lunar_date.display }}
          </div>

          <div class="mansion-keywords">
            <span
              v-for="kw in mansion.keywords"
              :key="kw"
              class="keyword-tag"
            >{{ kw }}</span>
          </div>

          <p class="mansion-personality">{{ mansion.personality }}</p>

          <button
            class="toggle-details"
            @click="showDetails = !showDetails"
          >
            {{ showDetails ? '收起詳情' : '查看詳情' }}
            <sl-icon :name="showDetails ? 'chevron-up' : 'chevron-down'"></sl-icon>
          </button>

          <div v-if="showDetails" class="mansion-details">
            <div class="detail-item">
              <h4>感情運</h4>
              <p>{{ mansion.love }}</p>
            </div>
            <div class="detail-item">
              <h4>事業運</h4>
              <p>{{ mansion.career }}</p>
            </div>
            <div class="detail-item">
              <h4>健康提醒</h4>
              <p>{{ mansion.health }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 相性診斷 -->
      <section class="compatibility-section card">
        <h2 class="section-title">雙人相性診斷</h2>
        <p class="section-desc">輸入兩人的生日，看看宿曜道怎麼說你們的緣分</p>

        <div class="compat-form">
          <div class="form-group">
            <sl-input
              type="date"
              v-model="date1"
              label="第一個人的生日"
              :max="new Date().toISOString().split('T')[0]"
            ></sl-input>
          </div>
          <div class="form-group">
            <sl-input
              type="date"
              v-model="date2"
              label="第二個人的生日"
              :max="new Date().toISOString().split('T')[0]"
            ></sl-input>
          </div>
          <button
            class="btn-gold"
            @click="calculateCompatibility"
            :disabled="!date1 || !date2 || compatLoading"
          >
            <sl-spinner v-if="compatLoading"></sl-spinner>
            <span v-else>分析相性</span>
          </button>
        </div>

        <div v-if="compatError" class="error-msg">
          {{ compatError }}
        </div>

        <!-- 相性結果 -->
        <div v-if="compatibility" class="compat-result">
          <div class="compat-pair">
            <div class="person-card">
              <span class="person-mansion">{{ compatibility.person1.mansion }}</span>
              <span class="person-reading">{{ compatibility.person1.reading }}</span>
              <span class="person-element" :style="{ color: elementColors[compatibility.person1.element] }">
                {{ compatibility.person1.element }}
              </span>
            </div>
            <div class="compat-vs">
              <span class="relation-name">{{ compatibility.relation.name }}</span>
            </div>
            <div class="person-card">
              <span class="person-mansion">{{ compatibility.person2.mansion }}</span>
              <span class="person-reading">{{ compatibility.person2.reading }}</span>
              <span class="person-element" :style="{ color: elementColors[compatibility.person2.element] }">
                {{ compatibility.person2.element }}
              </span>
            </div>
          </div>

          <div class="compat-score" :class="getScoreLevel(compatibility.score).class">
            <span class="score-number">{{ compatibility.score }}</span>
            <span class="score-label">{{ getScoreLevel(compatibility.score).text }}</span>
          </div>

          <div class="compat-summary">
            <p>{{ compatibility.relation.description }}</p>
            <p class="advice"><strong>建議：</strong>{{ compatibility.relation.advice }}</p>
          </div>
        </div>
      </section>

      <!-- 介紹區塊 -->
      <section class="intro-section">
        <h2>關於宿曜道</h2>
        <div class="intro-grid">
          <div class="intro-item">
            <div class="intro-icon">&#9734;</div>
            <h3>27 宿星</h3>
            <p>源自印度，經空海傳入日本的真言宗占星術，以農曆生日對應 27 種本命宿星</p>
          </div>
          <div class="intro-item">
            <div class="intro-icon">&#9775;</div>
            <h3>三九秘法</h3>
            <p>命、業胎、榮親、友衰、安壞、危成六種關係，揭示兩人之間的緣分深淺</p>
          </div>
          <div class="intro-item">
            <div class="intro-icon">&#9788;</div>
            <h3>務實指引</h3>
            <p>不只是占卜，更提供人際關係的實用建議，幫助你經營更好的關係</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.page-header h1 {
  margin-bottom: var(--space-2);
}

.page-header p {
  color: var(--text-secondary);
}

.section-title {
  margin-bottom: var(--space-2);
  color: var(--stellar-gold);
}

.section-desc {
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
  font-size: 0.9rem;
}

/* 本命宿查詢 */
.lookup-section {
  max-width: 600px;
  margin: 0 auto var(--space-8);
}

.form-row {
  display: flex;
  gap: var(--space-4);
  align-items: flex-end;
}

.form-row sl-input {
  flex: 1;
}

.form-row .btn-gold {
  min-width: 100px;
  height: 40px;
}

.error-msg {
  color: #E85D4C;
  margin-top: var(--space-4);
  font-size: 0.9rem;
}

/* 本命宿結果 */
.mansion-result {
  margin-top: var(--space-6);
  padding-top: var(--space-6);
  border-top: 1px solid var(--border-default);
}

.mansion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.mansion-name-group {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
}

.mansion-name {
  font-size: 2rem;
  font-weight: 600;
  color: var(--stellar-gold);
}

.mansion-reading {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.mansion-element {
  display: inline-block;
  padding: var(--space-2) var(--space-4);
  background: var(--cosmos-night);
  border: 1px solid var(--element-color);
  color: var(--element-color);
  border-radius: var(--radius-md);
  font-weight: 500;
}

.lunar-date {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-bottom: var(--space-4);
}

.mansion-keywords {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.keyword-tag {
  padding: var(--space-1) var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.mansion-personality {
  line-height: 1.8;
  color: var(--text-primary);
}

.toggle-details {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-4);
  padding: var(--space-2) var(--space-4);
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toggle-details:hover {
  border-color: var(--stellar-gold);
  color: var(--stellar-gold);
}

.mansion-details {
  margin-top: var(--space-6);
  display: grid;
  gap: var(--space-4);
}

.detail-item {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.detail-item h4 {
  color: var(--stellar-gold);
  margin-bottom: var(--space-2);
  font-size: 0.9rem;
}

.detail-item p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
}

/* 相性診斷 */
.compatibility-section {
  max-width: 600px;
  margin: 0 auto var(--space-12);
}

.compat-form {
  display: grid;
  gap: var(--space-4);
}

.compat-form .btn-gold {
  margin-top: var(--space-2);
}

/* 相性結果 */
.compat-result {
  margin-top: var(--space-6);
  padding-top: var(--space-6);
  border-top: 1px solid var(--border-default);
}

.compat-pair {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.person-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  min-width: 120px;
}

.person-mansion {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
}

.person-reading {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: var(--space-1);
}

.person-element {
  font-size: 0.8rem;
  margin-top: var(--space-2);
}

.compat-vs {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.relation-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--stellar-gold);
  padding: var(--space-2) var(--space-4);
  border: 2px solid var(--stellar-gold);
  border-radius: var(--radius-md);
}

.compat-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--space-6);
}

.score-number {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 0.9rem;
  margin-top: var(--space-2);
}

.compat-score.excellent .score-number { color: #4A9B5A; }
.compat-score.excellent .score-label { color: #4A9B5A; }
.compat-score.good .score-number { color: var(--stellar-gold); }
.compat-score.good .score-label { color: var(--stellar-gold); }
.compat-score.fair .score-number { color: #E89B3C; }
.compat-score.fair .score-label { color: #E89B3C; }
.compat-score.warning .score-number { color: #E85D4C; }
.compat-score.warning .score-label { color: #E85D4C; }

.compat-summary {
  background: var(--cosmos-night);
  padding: var(--space-6);
  border-radius: var(--radius-md);
}

.compat-summary p {
  line-height: 1.8;
  color: var(--text-secondary);
}

.compat-summary .advice {
  margin-top: var(--space-4);
  color: var(--text-primary);
}

/* 介紹區塊 */
.intro-section {
  text-align: center;
}

.intro-section h2 {
  margin-bottom: var(--space-6);
  color: var(--text-secondary);
}

.intro-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-6);
}

.intro-item {
  padding: var(--space-6);
}

.intro-icon {
  font-size: 2.5rem;
  margin-bottom: var(--space-3);
}

.intro-item h3 {
  margin-bottom: var(--space-2);
  font-size: 1.1rem;
}

.intro-item p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

@media (max-width: 480px) {
  .form-row {
    flex-direction: column;
  }

  .form-row .btn-gold {
    width: 100%;
  }

  .compat-pair {
    flex-direction: column;
  }

  .person-card {
    width: 100%;
  }

  .mansion-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }
}
</style>
