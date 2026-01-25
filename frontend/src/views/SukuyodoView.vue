<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

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
  reading: string
  description: string
  detailed: string
  advice: string
  tips: string[]
  avoid: string[]
  good_for: string[]
}

interface Person {
  date: string
  mansion: string
  reading: string
  element: string
  element_reading: string
  element_traits: string
  keywords: string[]
  index: number
}

interface Calculation {
  distance: number
  formula: string
  element_relation: string
}

interface CompatibilityResult {
  person1: Person
  person2: Person
  relation: Relation
  calculation: Calculation
  score: number
  element_bonus: number
  summary: string
}

interface Metadata {
  name: string
  reading: string
  origin: string
  origin_reading: string
  founder: string
  founder_reading: string
  scripture: string
  scripture_reading: string
  method: string
  method_reading: string
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
const showCompatDetails = ref(false)

// 元資料
const metadata = ref<Metadata | null>(null)

// 顯示公式說明
const showFormula = ref(false)

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

onMounted(async () => {
  // 載入元資料
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/metadata`)
    if (res.ok) {
      metadata.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to load metadata')
  }
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
  showCompatDetails.value = false

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
        <h1>
          <ruby>宿曜道<rp>(</rp><rt>しゅくようどう</rt><rp>)</rp></ruby>
        </h1>
        <p>
          <ruby>真言宗<rp>(</rp><rt>しんごんしゅう</rt><rp>)</rp></ruby>の占星術
          - <ruby>空海<rp>(</rp><rt>くうかい</rt><rp>)</rp></ruby>が伝えた
          <ruby>宿曜經<rp>(</rp><rt>すくようきょう</rt><rp>)</rp></ruby>に基づく
        </p>
      </header>

      <!-- 本命宿查詢 -->
      <section class="lookup-section card card-gold">
        <h2 class="section-title">
          查詢<ruby>本命宿<rp>(</rp><rt>ほんみょうしゅく</rt><rp>)</rp></ruby>
        </h2>
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
              <ruby class="mansion-name">
                {{ mansion.name_jp }}<rp>(</rp><rt>{{ mansion.reading }}</rt><rp>)</rp>
              </ruby>
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
        <h2 class="section-title">
          雙人相性診斷（<ruby>三九秘法<rp>(</rp><rt>さんくひほう</rt><rp>)</rp></ruby>）
        </h2>
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
              <ruby class="person-mansion">
                {{ compatibility.person1.mansion }}<rp>(</rp><rt>{{ compatibility.person1.reading }}</rt><rp>)</rp>
              </ruby>
              <span class="person-element" :style="{ color: elementColors[compatibility.person1.element] }">
                <ruby>{{ compatibility.person1.element }}<rp>(</rp><rt>{{ compatibility.person1.element_reading }}</rt><rp>)</rp></ruby>
              </span>
              <span class="element-traits">{{ compatibility.person1.element_traits }}</span>
            </div>
            <div class="compat-vs">
              <ruby class="relation-name">
                {{ compatibility.relation.name }}<rp>(</rp><rt>{{ compatibility.relation.reading }}</rt><rp>)</rp>
              </ruby>
            </div>
            <div class="person-card">
              <ruby class="person-mansion">
                {{ compatibility.person2.mansion }}<rp>(</rp><rt>{{ compatibility.person2.reading }}</rt><rp>)</rp>
              </ruby>
              <span class="person-element" :style="{ color: elementColors[compatibility.person2.element] }">
                <ruby>{{ compatibility.person2.element }}<rp>(</rp><rt>{{ compatibility.person2.element_reading }}</rt><rp>)</rp></ruby>
              </span>
              <span class="element-traits">{{ compatibility.person2.element_traits }}</span>
            </div>
          </div>

          <div class="compat-score" :class="getScoreLevel(compatibility.score).class">
            <span class="score-number">{{ compatibility.score }}</span>
            <span class="score-label">{{ getScoreLevel(compatibility.score).text }}</span>
          </div>

          <!-- 計算說明 -->
          <div class="calculation-info">
            <div class="calc-item">
              <span class="calc-label">距離計算</span>
              <code>{{ compatibility.calculation.formula }}</code>
            </div>
            <div class="calc-item">
              <span class="calc-label">元素加成</span>
              <span>{{ compatibility.calculation.element_relation }}</span>
            </div>
          </div>

          <div class="compat-summary">
            <p class="description">{{ compatibility.relation.description }}</p>

            <div v-if="compatibility.relation.detailed" class="detailed-section">
              <p>{{ compatibility.relation.detailed }}</p>
            </div>

            <button
              class="toggle-details"
              @click="showCompatDetails = !showCompatDetails"
            >
              {{ showCompatDetails ? '收起詳細建議' : '查看詳細建議' }}
              <sl-icon :name="showCompatDetails ? 'chevron-up' : 'chevron-down'"></sl-icon>
            </button>

            <div v-if="showCompatDetails" class="compat-details">
              <div v-if="compatibility.relation.tips?.length" class="detail-block tips">
                <h4>相處建議</h4>
                <ul>
                  <li v-for="tip in compatibility.relation.tips" :key="tip">{{ tip }}</li>
                </ul>
              </div>

              <div v-if="compatibility.relation.avoid?.length" class="detail-block avoid">
                <h4>應該避免</h4>
                <ul>
                  <li v-for="item in compatibility.relation.avoid" :key="item">{{ item }}</li>
                </ul>
              </div>

              <div v-if="compatibility.relation.good_for?.length" class="detail-block good-for">
                <h4>適合的關係</h4>
                <div class="tag-list">
                  <span v-for="item in compatibility.relation.good_for" :key="item" class="tag">{{ item }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 公式說明區塊 -->
      <section class="formula-section card">
        <button class="formula-toggle" @click="showFormula = !showFormula">
          <h2>
            <ruby>月宿傍通曆<rp>(</rp><rt>げっしゅくぼうつうれき</rt><rp>)</rp></ruby>
            計算說明
          </h2>
          <sl-icon :name="showFormula ? 'chevron-up' : 'chevron-down'"></sl-icon>
        </button>

        <div v-if="showFormula" class="formula-content">
          <div class="formula-block">
            <h3>本命宿計算公式</h3>
            <div class="formula-steps">
              <div class="step">
                <span class="step-num">1</span>
                <span>將西曆生日轉換為農曆日期</span>
              </div>
              <div class="step">
                <span class="step-num">2</span>
                <span>查詢該農曆月份的「起始宿」</span>
              </div>
              <div class="step">
                <span class="step-num">3</span>
                <span>套用公式：<code>本命宿 = (起始宿 + 日 - 1) mod 27</code></span>
              </div>
            </div>

            <div class="month-table">
              <h4>月份起始宿對照表</h4>
              <div class="table-grid">
                <div class="table-row header">
                  <span>月份</span>
                  <span>起始宿</span>
                </div>
                <div class="table-row"><span>正月</span><span>危宿 (11)</span></div>
                <div class="table-row"><span>二月</span><span>壁宿 (13)</span></div>
                <div class="table-row"><span>三月</span><span>婁宿 (15)</span></div>
                <div class="table-row"><span>四月</span><span>昴宿 (17)</span></div>
                <div class="table-row"><span>五月</span><span>觜宿 (19)</span></div>
                <div class="table-row"><span>六月</span><span>井宿 (21)</span></div>
                <div class="table-row"><span>七月</span><span>星宿 (24)</span></div>
                <div class="table-row"><span>八月</span><span>角宿 (0)</span></div>
                <div class="table-row"><span>九月</span><span>氐宿 (2)</span></div>
                <div class="table-row"><span>十月</span><span>心宿 (4)</span></div>
                <div class="table-row"><span>十一月</span><span>斗宿 (7)</span></div>
                <div class="table-row"><span>十二月</span><span>女宿 (9)</span></div>
              </div>
            </div>
          </div>

          <div class="formula-block">
            <h3>
              <ruby>三九秘法<rp>(</rp><rt>さんくひほう</rt><rp>)</rp></ruby>
              相性計算
            </h3>
            <p class="formula-desc">根據兩人本命宿的距離判斷六種關係</p>
            <div class="formula-box">
              <code>距離 = min(|宿A - 宿B|, 27 - |宿A - 宿B|)</code>
            </div>

            <div class="relation-table">
              <h4>距離與關係對照</h4>
              <div class="relation-grid">
                <div class="relation-row">
                  <ruby class="rel-name">命<rp>(</rp><rt>めい</rt><rp>)</rp></ruby>
                  <span class="rel-dist">距離 0</span>
                </div>
                <div class="relation-row">
                  <ruby class="rel-name">業胎<rp>(</rp><rt>ぎょうたい</rt><rp>)</rp></ruby>
                  <span class="rel-dist">距離 9, 18</span>
                </div>
                <div class="relation-row">
                  <ruby class="rel-name">栄親<rp>(</rp><rt>えいしん</rt><rp>)</rp></ruby>
                  <span class="rel-dist">距離 1, 3, 10, 12...</span>
                </div>
                <div class="relation-row">
                  <ruby class="rel-name">友衰<rp>(</rp><rt>ゆうすい</rt><rp>)</rp></ruby>
                  <span class="rel-dist">距離 2, 5, 11, 13...</span>
                </div>
                <div class="relation-row">
                  <ruby class="rel-name">安壊<rp>(</rp><rt>あんかい</rt><rp>)</rp></ruby>
                  <span class="rel-dist">距離 4, 6, 21, 23</span>
                </div>
                <div class="relation-row">
                  <ruby class="rel-name">危成<rp>(</rp><rt>きせい</rt><rp>)</rp></ruby>
                  <span class="rel-dist">距離 7, 8, 19, 20</span>
                </div>
              </div>
            </div>
          </div>

          <div class="formula-block">
            <h3>元素相性加成</h3>
            <p class="formula-desc">五行相生帶來額外加分</p>
            <div class="element-cycle">
              <span>木</span> → <span>火</span> → <span>土</span> → <span>金</span> → <span>水</span> → <span>木</span>
            </div>
            <ul class="bonus-list">
              <li><strong>同元素：</strong>+10 分</li>
              <li><strong>相生關係：</strong>+5 分</li>
              <li><strong>其他：</strong>無加成</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 介紹區塊 -->
      <section class="intro-section">
        <h2>關於<ruby>宿曜道<rp>(</rp><rt>しゅくようどう</rt><rp>)</rp></ruby></h2>
        <div class="intro-grid">
          <div class="intro-item">
            <div class="intro-icon">&#9734;</div>
            <h3><ruby>二十七宿<rp>(</rp><rt>にじゅうしちしゅく</rt><rp>)</rp></ruby></h3>
            <p>源自印度，經<ruby>空海<rp>(</rp><rt>くうかい</rt><rp>)</rp></ruby>傳入日本的<ruby>真言宗<rp>(</rp><rt>しんごんしゅう</rt><rp>)</rp></ruby>占星術，以農曆生日對應 27 種本命宿星</p>
          </div>
          <div class="intro-item">
            <div class="intro-icon">&#9775;</div>
            <h3><ruby>三九秘法<rp>(</rp><rt>さんくひほう</rt><rp>)</rp></ruby></h3>
            <p>
              <ruby>命<rp>(</rp><rt>めい</rt><rp>)</rp></ruby>、
              <ruby>業胎<rp>(</rp><rt>ぎょうたい</rt><rp>)</rp></ruby>、
              <ruby>栄親<rp>(</rp><rt>えいしん</rt><rp>)</rp></ruby>、
              <ruby>友衰<rp>(</rp><rt>ゆうすい</rt><rp>)</rp></ruby>、
              <ruby>安壊<rp>(</rp><rt>あんかい</rt><rp>)</rp></ruby>、
              <ruby>危成<rp>(</rp><rt>きせい</rt><rp>)</rp></ruby>
              六種關係，揭示兩人之間的緣分深淺
            </p>
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

.page-header h1 ruby {
  font-size: 2.5rem;
}

.page-header h1 rt {
  font-size: 0.5em;
  color: var(--text-muted);
}

.page-header p {
  color: var(--text-secondary);
}

.page-header p ruby rt {
  font-size: 0.7em;
}

.section-title {
  margin-bottom: var(--space-2);
  color: var(--stellar-gold);
}

.section-title ruby rt {
  font-size: 0.5em;
}

.section-desc {
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
  font-size: 0.9rem;
}

/* Ruby 標註樣式 */
ruby {
  ruby-align: center;
}

ruby rt {
  font-size: 0.6em;
  color: var(--text-muted);
}

ruby rp {
  display: none;
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

.mansion-name rt {
  font-size: 0.4em;
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
  flex-wrap: wrap;
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
  max-width: 700px;
  margin: 0 auto var(--space-8);
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
  min-width: 140px;
}

.person-mansion {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
}

.person-mansion rt {
  font-size: 0.5em;
}

.person-element {
  font-size: 0.9rem;
  margin-top: var(--space-2);
}

.element-traits {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: var(--space-1);
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

.relation-name rt {
  font-size: 0.5em;
}

.compat-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--space-4);
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

/* 計算說明 */
.calculation-info {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
}

.calc-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.calc-label {
  color: var(--text-muted);
}

.calc-item code {
  background: var(--cosmos-night);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-family: monospace;
  color: var(--stellar-gold);
}

.compat-summary {
  background: var(--cosmos-night);
  padding: var(--space-6);
  border-radius: var(--radius-md);
}

.compat-summary .description {
  line-height: 1.8;
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.detailed-section {
  padding: var(--space-4);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.detailed-section p {
  line-height: 1.8;
  color: var(--text-secondary);
}

.compat-details {
  margin-top: var(--space-6);
  display: grid;
  gap: var(--space-4);
}

.detail-block {
  padding: var(--space-4);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.detail-block h4 {
  margin-bottom: var(--space-3);
  font-size: 0.9rem;
}

.detail-block.tips h4 { color: #4A9B5A; }
.detail-block.avoid h4 { color: #E85D4C; }
.detail-block.good-for h4 { color: var(--stellar-gold); }

.detail-block ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.detail-block li {
  padding: var(--space-2) 0;
  padding-left: var(--space-4);
  position: relative;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.detail-block li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--text-muted);
}

.tag-list {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.tag {
  padding: var(--space-1) var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  color: var(--stellar-gold);
}

/* 公式說明區塊 */
.formula-section {
  max-width: 700px;
  margin: 0 auto var(--space-12);
}

.formula-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  color: inherit;
}

.formula-toggle h2 {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.formula-toggle sl-icon {
  color: var(--text-muted);
}

.formula-content {
  margin-top: var(--space-6);
  display: grid;
  gap: var(--space-6);
}

.formula-block {
  padding: var(--space-6);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.formula-block h3 {
  color: var(--stellar-gold);
  margin-bottom: var(--space-4);
  font-size: 1rem;
}

.formula-desc {
  color: var(--text-muted);
  margin-bottom: var(--space-4);
  font-size: 0.9rem;
}

.formula-steps {
  display: grid;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.step {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--stellar-gold);
  color: var(--cosmos-night);
  border-radius: 50%;
  font-size: 0.8rem;
  font-weight: 600;
}

.step code {
  background: var(--cosmos-twilight);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-family: monospace;
  color: var(--stellar-gold);
}

.month-table, .relation-table {
  margin-top: var(--space-4);
}

.month-table h4, .relation-table h4 {
  color: var(--text-secondary);
  margin-bottom: var(--space-3);
  font-size: 0.9rem;
}

.table-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-1);
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.table-row.header {
  background: var(--stellar-gold);
  color: var(--cosmos-night);
  font-weight: 600;
}

.formula-box {
  background: var(--cosmos-twilight);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  text-align: center;
  margin-bottom: var(--space-4);
}

.formula-box code {
  font-family: monospace;
  color: var(--stellar-gold);
  font-size: 1rem;
}

.relation-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-2);
}

.relation-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-sm);
}

.rel-name {
  font-weight: 500;
  color: var(--text-primary);
}

.rel-dist {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.element-cycle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
}

.element-cycle span {
  padding: var(--space-1) var(--space-2);
  background: var(--cosmos-night);
  border-radius: var(--radius-sm);
}

.bonus-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.bonus-list li {
  padding: var(--space-2) 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
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
  line-height: 1.6;
}

@media (max-width: 600px) {
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

  .table-grid {
    grid-template-columns: 1fr;
  }

  .relation-grid {
    grid-template-columns: 1fr;
  }

  .calculation-info {
    flex-direction: column;
  }
}
</style>
