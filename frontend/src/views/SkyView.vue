<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useProfile, type Partner } from '../stores/profile'
import PartnerSelector from '../components/PartnerSelector.vue'

interface Planet {
  planet: string
  name_zh: string
  sign_code: string
  sign_name: string
  degree: number
  longitude: number
}

interface MoonPhase {
  phase_name_zh: string
  illumination: number
  phase_angle: number
}

interface RetroPlanet {
  planet: string
  name_zh: string
}

interface SkySummary {
  datetime: string
  moon_phase: MoonPhase
  retrograde_planets: RetroPlanet[]
  retrograde_count: number
  dominant_element: string
  dominant_element_zh: string
  element_distribution: Record<string, number>
  planet_positions: Planet[]
}

interface CompatibilityResult {
  sign1_name: string
  sign2_name: string
  overall_score: number
  aspect: {
    name: string
    harmony: number
    desc: string
  }
  element_compatibility: {
    element1: string
    element2: string
    score: number
    desc: string
  }
  sky_influence: {
    influences: string[]
    venus_retrograde: boolean
    mercury_retrograde: boolean
  }
  advice: string
}

const { profile, isProfileSet, myZodiac, primaryPartner, getPartnerZodiac } = useProfile()

const summary = ref<SkySummary | null>(null)
const compatibility = ref<CompatibilityResult | null>(null)
const loading = ref(true)
const loadingCompat = ref(false)
const error = ref('')

// 當前選擇的對象（預設為主要對象）
const selectedPartner = ref<Partner | null>(null)

const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'

onMounted(async () => {
  try {
    const res = await fetch(`${apiUrl}/api/astronomy/summary`)
    if (res.ok) {
      summary.value = await res.json()
    } else {
      error.value = '無法載入天象資料'
    }
  } catch (e) {
    error.value = '無法連線到伺服器'
  } finally {
    loading.value = false
  }

  // 初始化選擇的對象為主要對象
  if (primaryPartner.value) {
    selectedPartner.value = primaryPartner.value
  }

  // 如果有設定檔案，載入配對分析
  if (isProfileSet.value && selectedPartner.value) {
    await loadCompatibility()
  }
})

// 監聽選擇的對象變化
watch(selectedPartner, async (newPartner) => {
  if (newPartner && isProfileSet.value) {
    await loadCompatibility()
  }
})

async function loadCompatibility() {
  if (!profile.value.zodiacCode || !selectedPartner.value) return

  loadingCompat.value = true
  try {
    const res = await fetch(`${apiUrl}/api/compatibility/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sign1: profile.value.zodiacCode,
        sign2: selectedPartner.value.zodiacCode
      })
    })
    if (res.ok) {
      compatibility.value = await res.json()
    }
  } catch (e) {
    console.error('載入配對分析失敗')
  } finally {
    loadingCompat.value = false
  }
}

const elementColors: Record<string, string> = {
  fire: '#E85D4C',
  earth: '#8B7355',
  air: '#7CB3D9',
  water: '#5B8FA8'
}

const elementNames: Record<string, string> = {
  fire: '火象',
  earth: '土象',
  air: '風象',
  water: '水象'
}

// 判斷行星是否在用戶的星座
const myPlanets = computed(() => {
  if (!summary.value || !profile.value.zodiacCode) return []
  return summary.value.planet_positions.filter(p => p.sign_code === profile.value.zodiacCode)
})

const partnerPlanets = computed(() => {
  if (!summary.value || !selectedPartner.value) return []
  return summary.value.planet_positions.filter(p => p.sign_code === selectedPartner.value!.zodiacCode)
})

// 生成個人化天象解讀
const personalizedInsight = computed(() => {
  if (!summary.value || !isProfileSet.value) return null

  const insights: string[] = []

  // 月相影響
  const moonPhase = summary.value.moon_phase.phase_name_zh
  if (moonPhase.includes('滿月')) {
    insights.push('滿月時期情感能量達到高峰，適合表達心意')
  } else if (moonPhase.includes('新月')) {
    insights.push('新月時期是開啟新關係的好時機')
  }

  // 逆行影響
  const venus = summary.value.retrograde_planets.find(p => p.planet === 'venus')
  const mercury = summary.value.retrograde_planets.find(p => p.planet === 'mercury')

  if (venus) {
    insights.push('金星逆行中，舊情人可能出現，感情需審慎')
  }
  if (mercury) {
    insights.push('水星逆行中，溝通容易出錯，表達時多確認')
  }

  // 行星在用戶星座
  if (myPlanets.value.length > 0) {
    const names = myPlanets.value.map(p => p.name_zh).join('、')
    insights.push(`${names}正經過你的星座，個人能量充沛`)
  }

  // 行星在對象星座
  if (partnerPlanets.value.length > 0 && selectedPartner.value) {
    const names = partnerPlanets.value.map(p => p.name_zh).join('、')
    const zodiac = getPartnerZodiac(selectedPartner.value)?.name || ''
    insights.push(`${names}正經過${zodiac}，對方近期狀態活躍`)
  }

  return insights.length > 0 ? insights : ['今日天象平穩，適合穩定發展']
})

function getScoreStars(score: number): string {
  const full = Math.floor(score)
  const half = score % 1 >= 0.5 ? 1 : 0
  return '\u2605'.repeat(full) + (half ? '\u2606' : '') + '\u2606'.repeat(5 - full - half)
}

// 月相說明
const moonPhaseExplanation = computed(() => {
  if (!summary.value) return ''
  const phase = summary.value.moon_phase.phase_name_zh
  const illumination = summary.value.moon_phase.illumination

  if (phase.includes('新月')) {
    return '月亮與太陽同方向，能量收斂。適合內省、許願、開始新計畫。感情上是重新出發的好時機。'
  } else if (phase.includes('上弦')) {
    return '月亮漸盈，能量逐漸增強。適合執行計畫、積極行動。感情上可以主動出擊。'
  } else if (phase.includes('滿月')) {
    return '月亮最圓，情緒能量達到高峰。容易情緒波動，但也適合表達心意、收穫成果。'
  } else if (phase.includes('下弦')) {
    return '月亮漸虧，能量逐漸收束。適合反省、整理、放下。感情上可以釐清關係。'
  }
  return `月亮亮度 ${illumination}%，能量處於過渡期，觀察內心變化。`
})

// 逆行說明
const retrogradeExplanation = computed(() => {
  if (!summary.value) return ''
  const retros = summary.value.retrograde_planets

  if (retros.length === 0) {
    return '沒有行星逆行，整體能量順暢，適合推進事務。'
  }

  const explanations: string[] = []
  for (const p of retros) {
    switch (p.planet) {
      case 'mercury':
        explanations.push('水星逆行：溝通、交通、電子設備容易出狀況。多確認訊息，簽約前仔細看條款。')
        break
      case 'venus':
        explanations.push('金星逆行：舊情人可能出現，審視感情價值觀。不建議開始新戀情或大額消費。')
        break
      case 'mars':
        explanations.push('火星逆行：行動力下降，容易衝動後悔。適合規劃而非立即行動。')
        break
      case 'jupiter':
        explanations.push('木星逆行：向內探索成長，機會需要耐心等待。')
        break
      case 'saturn':
        explanations.push('土星逆行：重新審視責任與限制，適合解決舊問題。')
        break
      default:
        explanations.push(`${p.name_zh}逆行：該領域能量向內轉化。`)
    }
  }
  return explanations.join('\n')
})

// 元素說明
const elementExplanation = computed(() => {
  if (!summary.value) return ''
  const dominant = summary.value.dominant_element

  const descriptions: Record<string, string> = {
    fire: '火象能量主導：整體氛圍積極、熱情、有衝勁。火象星座（牡羊、獅子、射手）狀態活躍，其他星座也會感染到這股熱情。',
    earth: '土象能量主導：整體氛圍務實、穩定、重視實際。土象星座（金牛、處女、魔羯）狀態舒適，適合處理實務工作。',
    air: '風象能量主導：整體氛圍活潑、善於溝通、思維敏捷。風象星座（雙子、天秤、水瓶）狀態出色，社交互動順暢。',
    water: '水象能量主導：整體氛圍敏感、直覺強、情感豐富。水象星座（巨蟹、天蠍、雙魚）狀態敏銳，容易感應他人情緒。'
  }

  return descriptions[dominant] || '能量均衡分布。'
})

// 行星說明
const planetMeanings: Record<string, string> = {
  sun: '太陽：代表自我、活力、生命力。太陽所在星座會影響整體的能量氛圍。',
  moon: '月亮：代表情緒、直覺、內在需求。月亮所在星座影響當下的情緒狀態。',
  mercury: '水星：代表溝通、思維、學習。水星所在星座影響表達方式與理解能力。',
  venus: '金星：代表愛情、美感、價值觀。金星所在星座影響感情運與審美。',
  mars: '火星：代表行動力、競爭、慾望。火星所在星座影響做事方式與動力。',
  jupiter: '木星：代表幸運、擴張、智慧。木星所在星座帶來該領域的好運。',
  saturn: '土星：代表責任、限制、成熟。土星所在星座需要面對的課題。',
  uranus: '天王星：代表變革、創新、自由。天王星所在星座帶來突破。',
  neptune: '海王星：代表夢想、靈感、迷幻。海王星所在星座帶來想像力。',
  pluto: '冥王星：代表轉化、重生、深層力量。冥王星所在星座帶來深度變化。'
}

function getPlanetMeaning(planet: string): string {
  return planetMeanings[planet] || ''
}
</script>

<template>
  <div class="sky-page">
    <div class="container">
      <header class="page-header">
        <h1>今日天象</h1>
        <p>基於 NASA 星曆資料的即時行星位置</p>
      </header>

      <div v-if="loading" class="loading">
        <sl-spinner style="font-size: 2rem;"></sl-spinner>
      </div>

      <div v-else-if="error" class="error">
        <sl-alert variant="danger" open>
          <sl-icon slot="icon" name="exclamation-triangle"></sl-icon>
          {{ error }}
        </sl-alert>
      </div>

      <div v-else-if="summary" class="sky-content">
        <!-- 個人化分析區塊 -->
        <section v-if="isProfileSet" class="personal-section card card-gold">
          <div class="personal-header">
            <span class="my-zodiac">{{ myZodiac?.symbol }}</span>
            <h2>{{ myZodiac?.name }} 今日天象解讀</h2>
          </div>

          <ul class="insight-list">
            <li v-for="(insight, i) in personalizedInsight" :key="i">
              {{ insight }}
            </li>
          </ul>

          <!-- 配對分析 -->
          <div v-if="profile.partners.length > 0" class="compat-section">
            <!-- 對象選擇器 -->
            <PartnerSelector v-model="selectedPartner" />

            <div v-if="selectedPartner && compatibility" class="compat-content">
              <div class="compat-header">
                <span class="zodiac-pair">
                  {{ myZodiac?.symbol }} &hearts; {{ getPartnerZodiac(selectedPartner)?.symbol }}
                </span>
                <span class="compat-score">{{ getScoreStars(compatibility.overall_score) }}</span>
              </div>

              <p class="compat-name">
                與{{ selectedPartner.nickname || getPartnerZodiac(selectedPartner)?.name }}的今日互動
              </p>

              <div class="compat-details">
                <span class="compat-aspect">{{ compatibility.aspect.name }}</span>
                <span class="compat-element">
                  {{ elementNames[compatibility.element_compatibility.element1] }} &times;
                  {{ elementNames[compatibility.element_compatibility.element2] }}
                </span>
              </div>

              <p class="compat-advice">{{ compatibility.advice }}</p>

              <div v-if="compatibility.sky_influence.influences.length > 0" class="sky-notes">
                <p v-for="(note, i) in compatibility.sky_influence.influences" :key="i" class="sky-note">
                  <sl-icon name="info-circle"></sl-icon>
                  {{ note }}
                </p>
              </div>
            </div>

            <div v-else-if="loadingCompat" class="loading-compat">
              <sl-spinner></sl-spinner>
              載入配對分析中...
            </div>
          </div>

          <div v-else class="no-partner">
            <router-link to="/profile" class="add-partner-link">
              <sl-icon name="plus-circle"></sl-icon>
              新增關注對象，查看配對分析
            </router-link>
          </div>
        </section>

        <!-- 未設定檔案提示 -->
        <section v-else class="setup-prompt card">
          <sl-icon name="person-plus"></sl-icon>
          <p>設定你的星座，獲得個人化天象解讀</p>
          <router-link to="/profile" class="btn-gold">
            設定我的資料
          </router-link>
        </section>

        <div class="highlight-cards">
          <div class="highlight-card card">
            <div class="highlight-icon">&#127769;</div>
            <h3>月相</h3>
            <p class="highlight-value">{{ summary.moon_phase.phase_name_zh }}</p>
            <p class="highlight-sub">亮度 {{ summary.moon_phase.illumination }}%</p>
            <p class="highlight-explanation">{{ moonPhaseExplanation }}</p>
          </div>

          <div class="highlight-card card">
            <div class="highlight-icon">&#128260;</div>
            <h3>逆行行星</h3>
            <p class="highlight-value">
              {{ summary.retrograde_count > 0 ? summary.retrograde_count + ' 顆' : '無' }}
            </p>
            <p v-if="summary.retrograde_count > 0" class="highlight-sub">
              {{ summary.retrograde_planets.map(p => p.name_zh).join('、') }}
            </p>
            <p class="highlight-explanation">{{ retrogradeExplanation }}</p>
          </div>

          <div class="highlight-card card">
            <div
              class="highlight-icon"
              :style="{ color: elementColors[summary.dominant_element] }"
            >
              &#9728;
            </div>
            <h3>主導元素</h3>
            <p class="highlight-value">{{ summary.dominant_element_zh }}</p>
            <p class="highlight-sub">能量分布最高</p>
            <p class="highlight-explanation">{{ elementExplanation }}</p>
          </div>
        </div>

        <section class="element-section card">
          <h2>元素能量分布</h2>
          <p class="section-desc">
            行星分布在 12 星座中，每個星座屬於四元素之一。元素分布反映當前宇宙能量的傾向。
          </p>
          <div class="element-bars">
            <div
              v-for="(count, element) in summary.element_distribution"
              :key="element"
              class="element-bar"
            >
              <div class="element-label">
                <span
                  class="element-dot"
                  :style="{ background: elementColors[element] }"
                ></span>
                {{ elementNames[element] }}
              </div>
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :style="{
                    width: (count / 10 * 100) + '%',
                    background: elementColors[element]
                  }"
                ></div>
              </div>
              <span class="element-count">{{ count }}</span>
            </div>
          </div>
        </section>

        <section class="planets-section">
          <h2>行星位置</h2>
          <p class="section-desc">
            點擊行星卡片查看該行星的意義。行星進入你的星座時，代表該領域能量增強。
          </p>
          <div class="planets-grid">
            <sl-tooltip
              v-for="planet in summary.planet_positions"
              :key="planet.planet"
              :content="getPlanetMeaning(planet.planet)"
              hoist
            >
              <div
                :class="[
                  'planet-card card',
                  {
                    'my-sign': planet.sign_code === profile.zodiacCode,
                    'partner-sign': selectedPartner && planet.sign_code === selectedPartner.zodiacCode
                  }
                ]"
              >
                <div class="planet-name">{{ planet.name_zh }}</div>
                <div class="planet-sign">{{ planet.sign_name }}</div>
                <div class="planet-degree">{{ planet.degree.toFixed(1) }}°</div>
                <div v-if="planet.sign_code === profile.zodiacCode" class="planet-tag my">我</div>
                <div v-else-if="selectedPartner && planet.sign_code === selectedPartner.zodiacCode" class="planet-tag partner">TA</div>
              </div>
            </sl-tooltip>
          </div>

          <!-- 行星與星座關係說明 -->
          <div class="planets-guide">
            <h3>行星如何影響你？</h3>
            <ul class="guide-list">
              <li><strong>標記「我」的行星</strong>：正經過你的星座，該行星代表的能量會特別強烈。例如金星經過，感情運提升；火星經過，行動力增強。</li>
              <li><strong>標記「TA」的行星</strong>：正經過對方的星座，可以了解對方近期的狀態。</li>
              <li><strong>太陽位置</strong>：決定當前是什麼「星座月」。太陽在你的星座時，是你的生日月，整體運勢最旺。</li>
              <li><strong>月亮位置</strong>：影響每 2-3 天的情緒氛圍。月亮在你的星座時，情感敏銳度提高。</li>
            </ul>
          </div>
        </section>

        <p class="data-source">
          資料來源：Skyfield + NASA DE421 星曆<br />
          計算時間：{{ new Date(summary.datetime).toLocaleString('zh-TW') }}
        </p>
      </div>
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

.loading,
.error {
  text-align: center;
  padding: var(--space-12);
}

/* 個人化區塊 */
.personal-section {
  margin-bottom: var(--space-6);
  padding: var(--space-6);
}

.personal-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.my-zodiac {
  font-size: 2rem;
}

.personal-header h2 {
  font-size: 1.1rem;
  color: var(--stellar-gold);
}

.insight-list {
  list-style: none;
  padding: 0;
  margin: 0 0 var(--space-5) 0;
}

.insight-list li {
  padding: var(--space-2) 0;
  padding-left: var(--space-4);
  border-left: 2px solid var(--border-gold);
  margin-bottom: var(--space-2);
  color: var(--text-secondary);
}

/* 配對區塊 */
.compat-section {
  padding-top: var(--space-5);
  border-top: 1px solid var(--border-gold);
}

.compat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.zodiac-pair {
  font-size: 1.5rem;
}

.compat-score {
  color: var(--stellar-gold);
  font-size: 1.1rem;
  letter-spacing: 2px;
}

.compat-name {
  font-weight: 500;
  margin-bottom: var(--space-3);
}

.compat-details {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.compat-aspect,
.compat-element {
  padding: var(--space-1) var(--space-3);
  background: var(--astral-deep);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.compat-advice {
  color: var(--text-primary);
  line-height: 1.7;
  margin-bottom: var(--space-4);
  white-space: pre-line;
}

.sky-notes {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.sky-note {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  font-size: 0.85rem;
  color: var(--text-muted);
}

.loading-compat {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--text-muted);
  padding: var(--space-4) 0;
}

.no-partner {
  padding-top: var(--space-4);
  border-top: 1px dashed var(--border-gold);
}

.add-partner-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  color: var(--text-muted);
  padding: var(--space-3);
}

.add-partner-link:hover {
  color: var(--stellar-gold);
}

/* 設定提示 */
.setup-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-8);
  margin-bottom: var(--space-6);
  text-align: center;
}

.setup-prompt sl-icon {
  font-size: 2.5rem;
  color: var(--text-muted);
}

.setup-prompt p {
  color: var(--text-secondary);
}

.setup-prompt .btn-gold {
  padding: var(--space-2) var(--space-6);
}

/* 高亮卡片 */
.highlight-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.highlight-card {
  text-align: center;
  padding: var(--space-6);
}

.highlight-icon {
  font-size: 2.5rem;
  margin-bottom: var(--space-3);
}

.highlight-card h3 {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}

.highlight-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--stellar-gold);
  margin-bottom: var(--space-1);
}

.highlight-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.highlight-explanation {
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-subtle);
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
  text-align: left;
  white-space: pre-line;
}

.section-desc {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: var(--space-4);
}

/* 元素分布 */
.element-section {
  margin-bottom: var(--space-8);
}

.element-section h2 {
  margin-bottom: var(--space-6);
}

.element-bars {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.element-bar {
  display: grid;
  grid-template-columns: 80px 1fr 40px;
  gap: var(--space-4);
  align-items: center;
}

.element-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.element-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.bar-track {
  height: 8px;
  background: var(--cosmos-twilight);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

.element-count {
  text-align: right;
  color: var(--text-muted);
}

/* 行星 */
.planets-section h2 {
  margin-bottom: var(--space-6);
}

.planets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-8);
}

.planet-card {
  position: relative;
  text-align: center;
  padding: var(--space-4);
}

.planet-card.my-sign {
  border-color: var(--stellar-gold);
}

.planet-card.partner-sign {
  border-color: var(--astral-light);
}

.planet-name {
  font-weight: 500;
  margin-bottom: var(--space-2);
}

.planet-sign {
  color: var(--stellar-gold);
  font-size: 0.95rem;
  margin-bottom: var(--space-1);
}

.planet-degree {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.planet-tag {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.planet-tag.my {
  background: var(--stellar-gold);
  color: var(--cosmos-night);
}

.planet-tag.partner {
  background: var(--astral-light);
  color: var(--cosmos-night);
}

.data-source {
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.8;
}

/* 行星說明區 */
.planets-guide {
  margin-top: var(--space-6);
  padding: var(--space-5);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.planets-guide h3 {
  font-size: 1rem;
  color: var(--stellar-gold);
  margin-bottom: var(--space-3);
}

.guide-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.guide-list li {
  padding: var(--space-2) 0;
  padding-left: var(--space-4);
  border-left: 2px solid var(--border-gold);
  margin-bottom: var(--space-2);
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.guide-list li strong {
  color: var(--stellar-gold);
}
</style>
