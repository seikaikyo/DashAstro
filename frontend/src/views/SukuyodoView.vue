<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProfile, ZODIAC_SIGNS } from '../stores/profile'
import CollapsibleCard from '../components/CollapsibleCard.vue'

const { profile, myBirthDate, partnersWithBirthDate } = useProfile()

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

interface LunarDate {
  lunar_month: number
  lunar_month_name: string
  lunar_day: number
  display: string
}

interface CompatibleMansion {
  name_jp: string
  name_zh: string
  reading: string
  index: number
  element: string
  element_reading: string
  keywords: string[]
  personality: string
  lunar_dates: LunarDate[]
}

interface CompatibilityCategory {
  relation: string
  reading: string
  score: number
  description: string
  mansions: CompatibleMansion[]
}

interface CompatibilityFinderResult {
  your_mansion: {
    name_jp: string
    name_zh: string
    reading: string
    index: number
    element: string
    lunar_date: {
      year: number
      month: number
      day: number
      display: string
    }
  }
  best_for_marriage: CompatibilityCategory
  past_life_connection: CompatibilityCategory
  should_avoid: CompatibilityCategory
}

// 運勢相關介面
interface FortuneScores {
  overall: number
  career: number
  love: number
  health: number
  wealth: number
}

interface DailyFortune {
  date: string
  weekday: {
    name: string
    reading: string
    element: string
    planet: string
  }
  your_mansion: {
    name_jp: string
    reading: string
    element: string
    index: number
  }
  element_relation: {
    type: string
    description: string
  }
  fortune: FortuneScores
  advice: string
  lucky: {
    direction: string
    direction_reading: string
    color: string
    color_reading: string
    color_hex: string
    numbers: number[]
  }
}

interface MonthlyFortune {
  year: number
  month: number
  month_mansion: {
    name_jp: string
    reading: string
    index: number
    element: string
  }
  your_mansion: {
    name_jp: string
    reading: string
    element: string
    index: number
  }
  relation: {
    type: string
    name: string
    reading: string
    description: string
  }
  theme: {
    title: string
    focus: string
    element_boost: string
  }
  fortune: FortuneScores
  weekly: {
    week: number
    score: number
    focus: string
  }[]
  advice: string
}

interface YearlyFortune {
  year: number
  stem: {
    character: string
    reading: string
    element: string
    yin_yang: string
  }
  branch: {
    character: string
    name: string
    reading: string
    element: string
  }
  your_mansion: {
    name_jp: string
    reading: string
    element: string
    index: number
  }
  fortune: FortuneScores
  monthly_trend: {
    month: number
    score: number
  }[]
  opportunities: string[]
  warnings: string[]
  advice: string
}

interface WeeklyFortune {
  year: number
  week: number
  week_start: string
  week_end: string
  week_element: {
    name: string
    reading: string
    element: string
    planet: string
  }
  your_mansion: {
    name_jp: string
    reading: string
    element: string
    index: number
  }
  element_relation: {
    type: string
    description: string
  }
  fortune: FortuneScores
  daily_overview: {
    date: string
    weekday: string
    score: number
  }[]
  advice: string
  lucky: {
    direction: string
    direction_reading: string
    color: string
    color_reading: string
    color_hex: string
  }
}

const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'

// 本命宿查詢
const birthDate = ref('')
const mansion = ref<Mansion | null>(null)
const lookupLoading = ref(false)
const lookupError = ref('')

// 相性診斷
const date1 = ref('')
const date2 = ref('')
const compatibility = ref<CompatibilityResult | null>(null)
const compatLoading = ref(false)
const compatError = ref('')

// 元資料
const metadata = ref<Metadata | null>(null)

// 顯示公式說明
const showFormula = ref(false)

// 相性配對查詢
const compatFinder = ref<CompatibilityFinderResult | null>(null)
const finderLoading = ref(false)
const selectedMansion = ref<CompatibleMansion | null>(null)
const expandedLunarDates = ref<number[]>([])

// 運勢查詢
const dailyFortune = ref<DailyFortune | null>(null)
const weeklyFortune = ref<WeeklyFortune | null>(null)
const monthlyFortune = ref<MonthlyFortune | null>(null)
const yearlyFortune = ref<YearlyFortune | null>(null)
const fortuneLoading = ref(false)

// 求職離職指引
interface CareerCategory {
  name: string
  jobs: string[]
}
interface LuckyDay {
  date: string
  weekday: string
  score: number
  reason: string
}
interface CareerGuidance {
  your_mansion: {
    name_jp: string
    reading: string
    element: string
  }
  suitable_careers: CareerCategory[]
  career_traits: string
  lucky_days: {
    job_seeking: LuckyDay[]
    resignation: LuckyDay[]
  }
  avoid_days: LuckyDay[]
  general_advice: string
}
const careerGuidance = ref<CareerGuidance | null>(null)
const careerLoading = ref(false)

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
  compatFinder.value = null
  selectedMansion.value = null
  dailyFortune.value = null
  weeklyFortune.value = null
  monthlyFortune.value = null
  yearlyFortune.value = null
  careerGuidance.value = null

  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/mansion/${birthDate.value}`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        mansion.value = data.data
        // 同時查詢相容星宿和運勢
        fetchCompatibleMansions()
        fetchAllFortunes()
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

const fetchCompatibleMansions = async () => {
  if (!birthDate.value) return

  finderLoading.value = true

  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/compatibility-finder/${birthDate.value}`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        compatFinder.value = data.data
      }
    }
  } catch (e) {
    console.error('Failed to fetch compatible mansions')
  } finally {
    finderLoading.value = false
  }
}

// 運勢查詢函數
const fetchDailyFortune = async () => {
  if (!birthDate.value) return
  fortuneLoading.value = true

  const today = new Date().toISOString().split('T')[0]
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/fortune/daily/${today}?birth_date=${birthDate.value}`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        dailyFortune.value = data.data
      }
    }
  } catch (e) {
    console.error('Failed to fetch daily fortune')
  } finally {
    fortuneLoading.value = false
  }
}

const fetchWeeklyFortune = async () => {
  if (!birthDate.value) return
  fortuneLoading.value = true

  const now = new Date()
  // 計算 ISO 週數
  const jan4 = new Date(now.getFullYear(), 0, 4)
  const daysSinceJan4 = Math.floor((now.getTime() - jan4.getTime()) / 86400000)
  const week = Math.ceil((daysSinceJan4 + jan4.getDay() + 1) / 7)

  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/fortune/weekly/${now.getFullYear()}/${week}?birth_date=${birthDate.value}`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        weeklyFortune.value = data.data
      }
    }
  } catch (e) {
    console.error('Failed to fetch weekly fortune')
  } finally {
    fortuneLoading.value = false
  }
}

const fetchMonthlyFortune = async () => {
  if (!birthDate.value) return
  fortuneLoading.value = true

  const now = new Date()
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/fortune/monthly/${now.getFullYear()}/${now.getMonth() + 1}?birth_date=${birthDate.value}`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        monthlyFortune.value = data.data
      }
    }
  } catch (e) {
    console.error('Failed to fetch monthly fortune')
  } finally {
    fortuneLoading.value = false
  }
}

const fetchYearlyFortune = async () => {
  if (!birthDate.value) return
  fortuneLoading.value = true

  const year = new Date().getFullYear()
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/fortune/yearly/${year}?birth_date=${birthDate.value}`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        yearlyFortune.value = data.data
      }
    }
  } catch (e) {
    console.error('Failed to fetch yearly fortune')
  } finally {
    fortuneLoading.value = false
  }
}

const fetchAllFortunes = async () => {
  await Promise.all([
    fetchDailyFortune(),
    fetchWeeklyFortune(),
    fetchMonthlyFortune(),
    fetchYearlyFortune(),
    fetchCareerGuidance()
  ])
}

const fetchCareerGuidance = async () => {
  if (!birthDate.value) return
  careerLoading.value = true
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/career-guidance/${birthDate.value}`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        careerGuidance.value = data.data
      }
    }
  } catch (e) {
    console.error('Failed to fetch career guidance')
  } finally {
    careerLoading.value = false
  }
}

const getFortuneLevel = (score: number) => {
  if (score >= 90) return { text: '大吉', class: 'excellent' }
  if (score >= 75) return { text: '吉', class: 'good' }
  if (score >= 60) return { text: '中吉', class: 'fair' }
  if (score >= 45) return { text: '小吉', class: 'caution' }
  return { text: '凶', class: 'warning' }
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

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

interface LunarDate {
  lunar_month: number
  lunar_day: number
  display: string
  solar_dates?: { lunar_year: number; solar_date: string; display: string }[]
}

const toggleLunarDate = (ld: LunarDate) => {
  const idx = expandedLunarDates.value.indexOf(ld.lunar_month)
  if (idx >= 0) {
    expandedLunarDates.value.splice(idx, 1)
  } else {
    expandedLunarDates.value.push(ld.lunar_month)
  }
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

      <!-- 查詢區域 -->
      <section class="lookup-form card card-gold">
        <h2 class="section-title">
          查詢<ruby>本命宿<rp>(</rp><rt>ほんみょうしゅく</rt><rp>)</rp></ruby>
        </h2>
        <p class="section-desc">輸入你的西曆生日，系統會自動轉換為農曆並計算你的本命宿</p>

        <!-- 快速選擇收藏對象 -->
        <div v-if="myBirthDate || partnersWithBirthDate.length > 0" class="quick-select">
          <span class="quick-select-label">快速選擇：</span>
          <button
            v-if="myBirthDate"
            class="quick-select-btn"
            :class="{ active: birthDate === myBirthDate }"
            @click="birthDate = myBirthDate; lookupMansion()"
          >
            我
          </button>
          <button
            v-for="partner in partnersWithBirthDate"
            :key="partner.id"
            class="quick-select-btn"
            :class="{ active: birthDate === partner.birthDate }"
            @click="birthDate = partner.birthDate!; lookupMansion()"
          >
            {{ partner.nickname }}
          </button>
          <router-link to="/profile" class="quick-select-add">
            +
          </router-link>
        </div>

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
      </section>

      <!-- 結果區域 - 摺疊卡片式 -->
      <div v-if="mansion" class="results-cards">
        <!-- 本命宿卡片 - 預設展開 -->
        <CollapsibleCard
          :title="`本命宿：${mansion.name_jp}（${mansion.element}）`"
          :subtitle="mansion.lunar_date?.display"
          icon="star-fill"
          :default-open="true"
        >
          <div class="mansion-content">
            <div class="mansion-header-info" :style="{ '--element-color': mansionElementColor }">
              <ruby class="mansion-name-large">
                {{ mansion.name_jp }}<rp>(</rp><rt>{{ mansion.reading }}</rt><rp>)</rp>
              </ruby>
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

            <div class="mansion-details-grid">
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
        </CollapsibleCard>

        <!-- 尋找配對卡片 -->
        <CollapsibleCard
          v-if="compatFinder"
          title="尋找最佳配對"
          subtitle="點擊星宿查看詳情"
          icon="heart-fill"
          :default-open="false"
        >
          <div class="compat-finder-content">
            <div v-if="finderLoading" class="finder-loading">
              <sl-spinner></sl-spinner>
              <span>載入中...</span>
            </div>
            <template v-else>
              <!-- 最適合結婚 -->
              <div class="finder-category marriage">
                <div class="category-header">
                  <ruby class="category-name">
                    {{ compatFinder.best_for_marriage.relation }}<rp>(</rp><rt>{{ compatFinder.best_for_marriage.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="category-score excellent">{{ compatFinder.best_for_marriage.score }} 分</span>
                </div>
                <p class="category-desc">{{ compatFinder.best_for_marriage.description }}</p>
                <div class="mansion-grid">
                  <button
                    v-for="m in compatFinder.best_for_marriage.mansions"
                    :key="m.index"
                    class="mansion-chip"
                    :class="{ active: selectedMansion?.index === m.index }"
                    @click="selectedMansion = selectedMansion?.index === m.index ? null : m"
                  >
                    <ruby>{{ m.name_jp }}<rp>(</rp><rt>{{ m.reading }}</rt><rp>)</rp></ruby>
                    <span class="chip-element" :style="{ color: elementColors[m.element] }">{{ m.element }}</span>
                  </button>
                </div>
              </div>

              <!-- 前世之緣 -->
              <div class="finder-category past-life">
                <div class="category-header">
                  <ruby class="category-name">
                    {{ compatFinder.past_life_connection.relation }}<rp>(</rp><rt>{{ compatFinder.past_life_connection.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="category-score good">{{ compatFinder.past_life_connection.score }} 分</span>
                </div>
                <p class="category-desc">{{ compatFinder.past_life_connection.description }}</p>
                <div class="mansion-grid">
                  <button
                    v-for="m in compatFinder.past_life_connection.mansions"
                    :key="m.index"
                    class="mansion-chip"
                    :class="{ active: selectedMansion?.index === m.index }"
                    @click="selectedMansion = selectedMansion?.index === m.index ? null : m"
                  >
                    <ruby>{{ m.name_jp }}<rp>(</rp><rt>{{ m.reading }}</rt><rp>)</rp></ruby>
                    <span class="chip-element" :style="{ color: elementColors[m.element] }">{{ m.element }}</span>
                  </button>
                </div>
              </div>

              <!-- 需要避免 -->
              <div class="finder-category avoid">
                <div class="category-header">
                  <ruby class="category-name">
                    {{ compatFinder.should_avoid.relation }}<rp>(</rp><rt>{{ compatFinder.should_avoid.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="category-score warning">{{ compatFinder.should_avoid.score }} 分</span>
                </div>
                <p class="category-desc">{{ compatFinder.should_avoid.description }}</p>
                <div class="mansion-grid">
                  <button
                    v-for="m in compatFinder.should_avoid.mansions"
                    :key="m.index"
                    class="mansion-chip danger"
                    :class="{ active: selectedMansion?.index === m.index }"
                    @click="selectedMansion = selectedMansion?.index === m.index ? null : m"
                  >
                    <ruby>{{ m.name_jp }}<rp>(</rp><rt>{{ m.reading }}</rt><rp>)</rp></ruby>
                    <span class="chip-element" :style="{ color: elementColors[m.element] }">{{ m.element }}</span>
                  </button>
                </div>
              </div>

              <!-- 選中的宿位詳細資訊 -->
              <div v-if="selectedMansion" class="selected-mansion-detail">
                <div class="detail-header">
                  <ruby class="detail-name">
                    {{ selectedMansion.name_jp }}<rp>(</rp><rt>{{ selectedMansion.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="detail-element" :style="{ borderColor: elementColors[selectedMansion.element], color: elementColors[selectedMansion.element] }">
                    {{ selectedMansion.element }}
                  </span>
                </div>
                <div class="detail-keywords">
                  <span v-for="kw in selectedMansion.keywords" :key="kw" class="keyword-tag">{{ kw }}</span>
                </div>
                <p class="detail-personality">{{ selectedMansion.personality }}</p>

                <!-- 農曆生日對照 -->
                <div v-if="selectedMansion.lunar_dates?.length" class="lunar-dates-section">
                  <h5>對應農曆生日</h5>
                  <p class="lunar-dates-hint">找這些日期生的人就對了（點擊查看西曆對照）</p>
                  <div class="lunar-dates-list">
                    <div
                      v-for="ld in selectedMansion.lunar_dates"
                      :key="ld.lunar_month"
                      class="lunar-date-item"
                    >
                      <button
                        class="lunar-date-header"
                        @click="toggleLunarDate(ld)"
                      >
                        <span class="lunar-date-text">{{ ld.display }}</span>
                        <sl-icon :name="expandedLunarDates.includes(ld.lunar_month) ? 'chevron-up' : 'chevron-down'"></sl-icon>
                      </button>
                      <div
                        v-if="expandedLunarDates.includes(ld.lunar_month) && ld.solar_dates?.length"
                        class="solar-dates-grid"
                      >
                        <span
                          v-for="sd in ld.solar_dates"
                          :key="sd.lunar_year"
                          class="solar-date-chip"
                        >{{ sd.display }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </CollapsibleCard>

        <!-- 今日運勢卡片 -->
        <CollapsibleCard
          v-if="dailyFortune"
          title="今日運勢"
          :subtitle="dailyFortune.date"
          icon="sun-fill"
          :badge="`${dailyFortune.fortune.overall} ${getFortuneLevel(dailyFortune.fortune.overall).text}`"
          :badge-class="getFortuneLevel(dailyFortune.fortune.overall).class"
          :default-open="false"
        >
          <div class="fortune-content">
            <div class="fortune-header">
              <div class="fortune-date">
                <ruby class="weekday">
                  {{ dailyFortune.weekday.name }}<rp>(</rp><rt>{{ dailyFortune.weekday.reading }}</rt><rp>)</rp>
                </ruby>
              </div>
              <div class="element-match">
                <span class="match-label">元素：</span>
                <span class="match-value" :style="{ color: elementColors[dailyFortune.weekday.element] }">
                  {{ dailyFortune.weekday.element }}
                </span>
                <span class="match-desc">{{ dailyFortune.element_relation.description }}</span>
              </div>
            </div>

            <div class="fortune-overall" :class="getFortuneLevel(dailyFortune.fortune.overall).class">
              <span class="overall-score">{{ dailyFortune.fortune.overall }}</span>
              <span class="overall-label">{{ getFortuneLevel(dailyFortune.fortune.overall).text }}</span>
            </div>

            <div class="fortune-grid">
              <div class="fortune-item">
                <span class="fortune-name">事業</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: dailyFortune.fortune.career + '%' }"></div></div>
                <span class="fortune-value">{{ dailyFortune.fortune.career }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">感情</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: dailyFortune.fortune.love + '%' }"></div></div>
                <span class="fortune-value">{{ dailyFortune.fortune.love }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">健康</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: dailyFortune.fortune.health + '%' }"></div></div>
                <span class="fortune-value">{{ dailyFortune.fortune.health }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">財運</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: dailyFortune.fortune.wealth + '%' }"></div></div>
                <span class="fortune-value">{{ dailyFortune.fortune.wealth }}</span>
              </div>
            </div>

            <p class="fortune-advice">{{ dailyFortune.advice }}</p>

            <div class="lucky-items">
              <h4>幸運指南</h4>
              <div class="lucky-grid">
                <div class="lucky-item">
                  <span class="lucky-label">方位</span>
                  <ruby class="lucky-value">{{ dailyFortune.lucky.direction }}<rp>(</rp><rt>{{ dailyFortune.lucky.direction_reading }}</rt><rp>)</rp></ruby>
                </div>
                <div class="lucky-item">
                  <span class="lucky-label">顏色</span>
                  <span class="lucky-value"><span class="color-dot" :style="{ background: dailyFortune.lucky.color_hex }"></span>{{ dailyFortune.lucky.color }}</span>
                </div>
                <div class="lucky-item">
                  <span class="lucky-label">數字</span>
                  <span class="lucky-value">{{ dailyFortune.lucky.numbers.join(', ') }}</span>
                </div>
              </div>
            </div>
          </div>
        </CollapsibleCard>

        <!-- 本週運勢卡片 -->
        <CollapsibleCard
          v-if="weeklyFortune"
          title="本週運勢"
          :subtitle="`${weeklyFortune.week_start} ~ ${weeklyFortune.week_end}`"
          icon="calendar-week-fill"
          :badge="`${weeklyFortune.fortune.overall} ${getFortuneLevel(weeklyFortune.fortune.overall).text}`"
          :badge-class="getFortuneLevel(weeklyFortune.fortune.overall).class"
          :default-open="false"
        >
          <div class="fortune-content">
            <div class="fortune-header">
              <div class="fortune-date">
                <span class="week-num-label">第 {{ weeklyFortune.week }} 週</span>
              </div>
              <div class="element-match">
                <span class="match-label">週主宰：</span>
                <span class="match-value" :style="{ color: elementColors[weeklyFortune.week_element.element] }">
                  {{ weeklyFortune.week_element.element }}
                </span>
                <span class="match-desc">{{ weeklyFortune.element_relation.description }}</span>
              </div>
            </div>

            <div class="fortune-overall" :class="getFortuneLevel(weeklyFortune.fortune.overall).class">
              <span class="overall-score">{{ weeklyFortune.fortune.overall }}</span>
              <span class="overall-label">{{ getFortuneLevel(weeklyFortune.fortune.overall).text }}</span>
            </div>

            <div class="fortune-grid">
              <div class="fortune-item">
                <span class="fortune-name">事業</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: weeklyFortune.fortune.career + '%' }"></div></div>
                <span class="fortune-value">{{ weeklyFortune.fortune.career }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">感情</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: weeklyFortune.fortune.love + '%' }"></div></div>
                <span class="fortune-value">{{ weeklyFortune.fortune.love }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">健康</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: weeklyFortune.fortune.health + '%' }"></div></div>
                <span class="fortune-value">{{ weeklyFortune.fortune.health }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">財運</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: weeklyFortune.fortune.wealth + '%' }"></div></div>
                <span class="fortune-value">{{ weeklyFortune.fortune.wealth }}</span>
              </div>
            </div>

            <div class="daily-overview">
              <h4>每日概況</h4>
              <div class="daily-grid">
                <div v-for="d in weeklyFortune.daily_overview" :key="d.date" class="daily-item">
                  <span class="day-weekday">{{ d.weekday }}</span>
                  <span class="day-score" :class="getFortuneLevel(d.score).class">{{ d.score }}</span>
                </div>
              </div>
            </div>

            <p class="fortune-advice">{{ weeklyFortune.advice }}</p>

            <div class="lucky-items">
              <h4>幸運指南</h4>
              <div class="lucky-grid">
                <div class="lucky-item">
                  <span class="lucky-label">方位</span>
                  <ruby class="lucky-value">{{ weeklyFortune.lucky.direction }}<rp>(</rp><rt>{{ weeklyFortune.lucky.direction_reading }}</rt><rp>)</rp></ruby>
                </div>
                <div class="lucky-item">
                  <span class="lucky-label">顏色</span>
                  <span class="lucky-value"><span class="color-dot" :style="{ background: weeklyFortune.lucky.color_hex }"></span>{{ weeklyFortune.lucky.color }}</span>
                </div>
              </div>
            </div>
          </div>
        </CollapsibleCard>

        <!-- 本月運勢卡片 -->
        <CollapsibleCard
          v-if="monthlyFortune"
          title="本月運勢"
          :subtitle="`${monthlyFortune.year} 年 ${monthlyFortune.month} 月`"
          icon="calendar-fill"
          :badge="`${monthlyFortune.fortune.overall} ${getFortuneLevel(monthlyFortune.fortune.overall).text}`"
          :badge-class="getFortuneLevel(monthlyFortune.fortune.overall).class"
          :default-open="false"
        >
          <div class="fortune-content">
            <div class="fortune-header">
              <div class="month-theme">
                <span class="theme-title">{{ monthlyFortune.theme.title }}</span>
                <span class="theme-focus">重點：{{ monthlyFortune.theme.focus }}</span>
              </div>
            </div>

            <div class="month-relation">
              <span class="relation-label">月宿關係：</span>
              <ruby class="relation-name">
                {{ monthlyFortune.relation.name }}<rp>(</rp><rt>{{ monthlyFortune.relation.reading }}</rt><rp>)</rp>
              </ruby>
            </div>

            <div class="fortune-overall" :class="getFortuneLevel(monthlyFortune.fortune.overall).class">
              <span class="overall-score">{{ monthlyFortune.fortune.overall }}</span>
              <span class="overall-label">{{ getFortuneLevel(monthlyFortune.fortune.overall).text }}</span>
            </div>

            <div class="fortune-grid">
              <div class="fortune-item">
                <span class="fortune-name">事業</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: monthlyFortune.fortune.career + '%' }"></div></div>
                <span class="fortune-value">{{ monthlyFortune.fortune.career }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">感情</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: monthlyFortune.fortune.love + '%' }"></div></div>
                <span class="fortune-value">{{ monthlyFortune.fortune.love }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">健康</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: monthlyFortune.fortune.health + '%' }"></div></div>
                <span class="fortune-value">{{ monthlyFortune.fortune.health }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">財運</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: monthlyFortune.fortune.wealth + '%' }"></div></div>
                <span class="fortune-value">{{ monthlyFortune.fortune.wealth }}</span>
              </div>
            </div>

            <div class="weekly-breakdown">
              <h4>每週概況</h4>
              <div class="weekly-grid">
                <div v-for="w in monthlyFortune.weekly" :key="w.week" class="weekly-item">
                  <span class="week-num">第 {{ w.week }} 週</span>
                  <span class="week-score" :class="getFortuneLevel(w.score).class">{{ w.score }}</span>
                  <span class="week-focus">{{ w.focus }}</span>
                </div>
              </div>
            </div>

            <p class="fortune-advice">{{ monthlyFortune.advice }}</p>
          </div>
        </CollapsibleCard>

        <!-- 本年運勢卡片 -->
        <CollapsibleCard
          v-if="yearlyFortune"
          title="本年運勢"
          :subtitle="`${yearlyFortune.year} 年`"
          icon="calendar-range-fill"
          :badge="`${yearlyFortune.fortune.overall} ${getFortuneLevel(yearlyFortune.fortune.overall).text}`"
          :badge-class="getFortuneLevel(yearlyFortune.fortune.overall).class"
          :default-open="false"
        >
          <div class="fortune-content">
            <div class="fortune-header">
              <div class="year-info">
                <ruby class="stem-branch">
                  {{ yearlyFortune.stem.character }}{{ yearlyFortune.branch.character }}
                  <rp>(</rp><rt>{{ yearlyFortune.stem.reading }}{{ yearlyFortune.branch.reading }}</rt><rp>)</rp>
                </ruby>
                <span class="zodiac">{{ yearlyFortune.branch.name }}年</span>
              </div>
            </div>

            <div class="fortune-overall" :class="getFortuneLevel(yearlyFortune.fortune.overall).class">
              <span class="overall-score">{{ yearlyFortune.fortune.overall }}</span>
              <span class="overall-label">{{ getFortuneLevel(yearlyFortune.fortune.overall).text }}</span>
            </div>

            <div class="fortune-grid">
              <div class="fortune-item">
                <span class="fortune-name">事業</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: yearlyFortune.fortune.career + '%' }"></div></div>
                <span class="fortune-value">{{ yearlyFortune.fortune.career }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">感情</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: yearlyFortune.fortune.love + '%' }"></div></div>
                <span class="fortune-value">{{ yearlyFortune.fortune.love }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">健康</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: yearlyFortune.fortune.health + '%' }"></div></div>
                <span class="fortune-value">{{ yearlyFortune.fortune.health }}</span>
              </div>
              <div class="fortune-item">
                <span class="fortune-name">財運</span>
                <div class="fortune-bar"><div class="bar-fill" :style="{ width: yearlyFortune.fortune.wealth + '%' }"></div></div>
                <span class="fortune-value">{{ yearlyFortune.fortune.wealth }}</span>
              </div>
            </div>

            <div class="monthly-trend">
              <h4>月度趨勢</h4>
              <div class="trend-chart">
                <div
                  v-for="m in yearlyFortune.monthly_trend"
                  :key="m.month"
                  class="trend-bar"
                  :style="{ height: m.score + '%' }"
                  :class="getFortuneLevel(m.score).class"
                >
                  <span class="trend-value">{{ m.score }}</span>
                </div>
              </div>
              <div class="trend-labels">
                <span v-for="i in 12" :key="i">{{ i }}月</span>
              </div>
            </div>

            <div v-if="yearlyFortune.opportunities.length" class="opportunities">
              <h4>機會提示</h4>
              <ul>
                <li v-for="(opp, idx) in yearlyFortune.opportunities" :key="idx">{{ opp }}</li>
              </ul>
            </div>

            <div v-if="yearlyFortune.warnings.length" class="warnings">
              <h4>注意事項</h4>
              <ul>
                <li v-for="(warn, idx) in yearlyFortune.warnings" :key="idx">{{ warn }}</li>
              </ul>
            </div>

            <p class="fortune-advice">{{ yearlyFortune.advice }}</p>
          </div>
        </CollapsibleCard>

        <!-- 雙人相性診斷卡片 -->
        <CollapsibleCard
          title="雙人相性診斷"
          subtitle="輸入兩人生日分析緣分"
          icon="people-fill"
          :badge="compatibility ? `${compatibility.score} ${getScoreLevel(compatibility.score).text}` : undefined"
          :badge-class="compatibility ? getScoreLevel(compatibility.score).class : ''"
          :default-open="false"
        >
          <div class="compat-content">
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

                <div class="compat-details">
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
          </div>
        </CollapsibleCard>

        <!-- 求職離職指引卡片 -->
        <CollapsibleCard
          title="求職離職指引"
          subtitle="適合職業與吉日查詢"
          icon="briefcase"
          :badge="careerGuidance ? '已載入' : undefined"
          :default-open="false"
        >
          <div class="career-content">
            <template v-if="careerLoading">
              <div class="loading-state">
                <sl-spinner></sl-spinner>
                <span>載入中...</span>
              </div>
            </template>

            <template v-else-if="careerGuidance">
              <!-- 適合職業類型 -->
              <div class="career-section">
                <h4>適合的職業類型</h4>
                <p class="career-traits">{{ careerGuidance.career_traits }}</p>
                <div class="career-categories">
                  <div
                    v-for="category in careerGuidance.suitable_careers"
                    :key="category.name"
                    class="career-category"
                  >
                    <span class="category-name">{{ category.name }}</span>
                    <div class="job-list">
                      <span v-for="job in category.jobs" :key="job" class="job-tag">{{ job }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 職涯建議 -->
              <div class="career-advice">
                <p>{{ careerGuidance.general_advice }}</p>
              </div>

              <!-- 求職吉日 -->
              <div class="lucky-days-section">
                <h4>近 30 天求職吉日</h4>
                <div v-if="careerGuidance.lucky_days.job_seeking.length" class="lucky-days-list">
                  <div
                    v-for="day in careerGuidance.lucky_days.job_seeking"
                    :key="day.date"
                    class="lucky-day-item seeking"
                  >
                    <span class="day-date">{{ formatDate(day.date) }} ({{ day.weekday }})</span>
                    <span class="day-score">{{ day.score }}分</span>
                    <span class="day-reason">{{ day.reason }}</span>
                  </div>
                </div>
                <p v-else class="no-data">暫無特別吉日</p>
              </div>

              <!-- 離職吉日 -->
              <div class="lucky-days-section">
                <h4>近 30 天離職吉日</h4>
                <div v-if="careerGuidance.lucky_days.resignation.length" class="lucky-days-list">
                  <div
                    v-for="day in careerGuidance.lucky_days.resignation"
                    :key="day.date"
                    class="lucky-day-item resignation"
                  >
                    <span class="day-date">{{ formatDate(day.date) }} ({{ day.weekday }})</span>
                    <span class="day-score">{{ day.score }}分</span>
                    <span class="day-reason">{{ day.reason }}</span>
                  </div>
                </div>
                <p v-else class="no-data">暫無適合日期</p>
              </div>

              <!-- 需避開的日子 -->
              <div v-if="careerGuidance.avoid_days.length" class="avoid-days-section">
                <h4>需避開的日子</h4>
                <div class="avoid-days-list">
                  <div
                    v-for="day in careerGuidance.avoid_days"
                    :key="day.date"
                    class="avoid-day-item"
                  >
                    <span class="day-date">{{ formatDate(day.date) }} ({{ day.weekday }})</span>
                    <span class="day-reason">{{ day.reason }}</span>
                  </div>
                </div>
              </div>
            </template>

            <template v-else>
              <p class="no-data">請先查詢本命宿以取得求職離職指引</p>
            </template>
          </div>
        </CollapsibleCard>
      </div>

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

/* 查詢表單 */
.lookup-form {
  max-width: 600px;
  margin: 0 auto var(--space-8);
}

.quick-select {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  padding: var(--space-3);
  background: var(--cosmos-dusk);
  border-radius: var(--radius-md);
}

.quick-select-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.quick-select-btn {
  padding: var(--space-1) var(--space-3);
  background: var(--cosmos-night);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-select-btn:hover {
  border-color: var(--stellar-gold);
  color: var(--stellar-gold);
}

.quick-select-btn.active {
  background: var(--stellar-gold);
  border-color: var(--stellar-gold);
  color: var(--cosmos-night);
}

.quick-select-add {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: none;
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-full);
  color: var(--text-muted);
  font-size: 1rem;
  text-decoration: none;
  transition: all 0.2s;
}

.quick-select-add:hover {
  border-color: var(--stellar-gold);
  color: var(--stellar-gold);
}

/* 結果區域 - 摺疊卡片佈局 */
.results-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-width: 800px;
  margin: 0 auto var(--space-8);
}

/* 本命宿內容 */
.mansion-content {
  padding-top: var(--space-2);
}

.mansion-header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.mansion-name-large {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--stellar-gold);
}

.mansion-name-large rt {
  font-size: 0.4em;
}

.mansion-details-grid {
  display: grid;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

/* 配對內容 */
.compat-finder-content,
.compat-content {
  padding-top: var(--space-2);
}

/* 運勢內容 */
.fortune-content {
  padding-top: var(--space-2);
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

/* 相性配對查詢 - 右側欄 */
.compat-finder-section {
  /* 獨立 card，不需要 border-top */
}

.finder-title {
  text-align: center;
  color: var(--stellar-gold);
  margin-bottom: var(--space-6);
  font-size: 1.2rem;
}

.finder-category {
  margin-bottom: var(--space-6);
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.category-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.category-icon {
  font-size: 1.2rem;
}

.category-name {
  font-size: 1.1rem;
  font-weight: 600;
}

.finder-category.marriage .category-name {
  color: #4A9B5A;
}

.finder-category.past-life .category-name {
  color: #9B7FCF;
}

.finder-category.avoid .category-name {
  color: #E89B3C;
}

.category-score {
  margin-left: auto;
  padding: var(--space-1) var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  color: var(--stellar-gold);
}

.category-score.warning {
  color: #E89B3C;
}

.category-desc {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: var(--space-4);
}

.mansion-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.mansion-chip {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-twilight);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.mansion-chip ruby rt {
  font-size: 0.6em;
}

.mansion-chip:hover {
  border-color: var(--stellar-gold);
}

.mansion-chip.active {
  border-color: var(--stellar-gold);
  background: rgba(199, 163, 101, 0.15);
}

.mansion-chip.danger {
  border-color: rgba(232, 93, 76, 0.3);
}

.mansion-chip.danger:hover,
.mansion-chip.danger.active {
  border-color: #E85D4C;
  background: rgba(232, 93, 76, 0.1);
}

.chip-element {
  font-size: 0.8rem;
  font-weight: 500;
}

.selected-mansion-detail {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
  border: 1px solid var(--stellar-gold);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.detail-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--stellar-gold);
}

.detail-name rt {
  font-size: 0.4em;
}

.detail-element {
  padding: var(--space-1) var(--space-3);
  border: 1px solid;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.detail-keywords {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  flex-wrap: wrap;
}

.detail-personality {
  line-height: 1.7;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* 農曆生日對照 */
.lunar-dates-section {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-default);
}

.lunar-dates-section h5 {
  color: var(--stellar-gold);
  font-size: 0.9rem;
  margin-bottom: var(--space-1);
}

.lunar-dates-hint {
  color: var(--text-muted);
  font-size: 0.8rem;
  margin-bottom: var(--space-3);
}

.lunar-dates-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.lunar-date-item {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.lunar-date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-night);
  border: none;
  cursor: pointer;
  color: var(--text-primary);
  transition: background 0.2s;
}

.lunar-date-header:hover {
  background: var(--cosmos-twilight);
}

.lunar-date-text {
  font-weight: 500;
}

.lunar-date-header sl-icon {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.solar-dates-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-twilight);
  max-height: 200px;
  overflow-y: auto;
}

.solar-date-chip {
  padding: var(--space-1) var(--space-2);
  background: var(--cosmos-night);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.lunar-dates-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.lunar-date-chip {
  padding: var(--space-1) var(--space-2);
  background: var(--cosmos-night);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  color: var(--text-primary);
}

.finder-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-4);
  color: var(--text-muted);
}

/* 運勢區塊 */
.fortune-section {
  max-width: 800px;
  margin: 0 auto var(--space-8);
}

.fortune-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  border-bottom: 1px solid var(--border-default);
  padding-bottom: var(--space-2);
}

.tab-btn {
  padding: var(--space-2) var(--space-4);
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.95rem;
  transition: all var(--transition-fast);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.tab-btn:hover {
  color: var(--stellar-gold);
}

.tab-btn.active {
  color: var(--stellar-gold);
  background: var(--cosmos-night);
  font-weight: 600;
}

.fortune-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-8);
  color: var(--text-muted);
}

.fortune-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.fortune-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
  gap: var(--space-3);
}

.fortune-date {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
}

.date-label {
  font-size: 1.1rem;
  color: var(--text-primary);
}

.weekday {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.weekday rt {
  font-size: 0.6em;
}

.element-match {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.match-label {
  color: var(--text-muted);
}

.match-value {
  font-weight: 600;
}

.match-desc {
  color: var(--text-secondary);
}

.fortune-overall {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  background: var(--cosmos-night);
  border-radius: var(--radius-lg);
}

.overall-score {
  font-size: 4rem;
  font-weight: 700;
  line-height: 1;
}

.overall-label {
  font-size: 1.1rem;
  margin-top: var(--space-2);
}

.fortune-overall.excellent .overall-score { color: #4A9B5A; }
.fortune-overall.excellent .overall-label { color: #4A9B5A; }
.fortune-overall.good .overall-score { color: var(--stellar-gold); }
.fortune-overall.good .overall-label { color: var(--stellar-gold); }
.fortune-overall.fair .overall-score { color: #7CB3D9; }
.fortune-overall.fair .overall-label { color: #7CB3D9; }
.fortune-overall.caution .overall-score { color: #E89B3C; }
.fortune-overall.caution .overall-label { color: #E89B3C; }
.fortune-overall.warning .overall-score { color: #E85D4C; }
.fortune-overall.warning .overall-label { color: #E85D4C; }

.fortune-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.fortune-item {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.fortune-icon {
  font-size: 1.2rem;
}

.fortune-name {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.fortune-bar {
  width: 100%;
  height: 6px;
  background: var(--cosmos-twilight);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--stellar-gold), #E89B3C);
  border-radius: var(--radius-full);
  transition: width 0.5s ease;
}

.fortune-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--stellar-gold);
  min-width: 30px;
  text-align: right;
}

.fortune-advice {
  padding: var(--space-4);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
  line-height: 1.7;
  color: var(--text-secondary);
  margin-bottom: var(--space-4);
  border-left: 3px solid var(--stellar-gold);
}

/* 幸運指南 */
.lucky-items {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.lucky-items h4 {
  color: var(--stellar-gold);
  margin-bottom: var(--space-3);
  font-size: 0.95rem;
}

.lucky-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.lucky-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-2);
}

.lucky-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: var(--space-1);
}

.lucky-value {
  font-size: 0.95rem;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

/* 月運勢 */
.month-theme {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.theme-title {
  font-size: 1rem;
  color: var(--stellar-gold);
  font-weight: 600;
}

.theme-focus {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.month-relation {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.relation-label {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.month-relation .relation-name {
  color: var(--stellar-gold);
  font-weight: 600;
}

.week-num-label {
  font-size: 0.85rem;
  color: var(--stellar-gold);
  margin-left: var(--space-2);
}

.daily-overview {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.daily-overview h4 {
  color: var(--stellar-gold);
  margin-bottom: var(--space-3);
  font-size: 0.95rem;
}

.daily-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: var(--space-2);
}

.daily-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-2);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.day-weekday {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-bottom: var(--space-1);
}

.day-score {
  font-size: 1.1rem;
  font-weight: 600;
}

.weekly-breakdown {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.weekly-breakdown h4 {
  color: var(--stellar-gold);
  margin-bottom: var(--space-3);
  font-size: 0.95rem;
}

.weekly-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}

.weekly-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-2);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.week-num {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.week-score {
  font-size: 1.3rem;
  font-weight: 700;
  margin: var(--space-1) 0;
}

.week-score.excellent { color: #4A9B5A; }
.week-score.good { color: var(--stellar-gold); }
.week-score.fair { color: #7CB3D9; }
.week-score.caution { color: #E89B3C; }
.week-score.warning { color: #E85D4C; }

.week-focus {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* 年運勢 */
.year-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.stem-branch {
  font-size: 1.1rem;
  color: var(--stellar-gold);
  font-weight: 600;
}

.stem-branch rt {
  font-size: 0.5em;
}

.zodiac {
  font-size: 0.9rem;
  color: var(--text-secondary);
  padding: var(--space-1) var(--space-2);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.monthly-trend {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.monthly-trend h4 {
  color: var(--stellar-gold);
  margin-bottom: var(--space-3);
  font-size: 0.95rem;
}

.trend-chart {
  display: flex;
  align-items: flex-end;
  gap: var(--space-1);
  height: 120px;
  padding: var(--space-2) 0;
}

.trend-bar {
  flex: 1;
  background: var(--cosmos-twilight);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  min-height: 20px;
  transition: height 0.5s ease;
}

.trend-bar.excellent { background: #4A9B5A; }
.trend-bar.good { background: var(--stellar-gold); }
.trend-bar.fair { background: #7CB3D9; }
.trend-bar.caution { background: #E89B3C; }
.trend-bar.warning { background: #E85D4C; }

.trend-value {
  font-size: 0.65rem;
  color: var(--cosmos-night);
  font-weight: 600;
  padding-top: var(--space-1);
}

.trend-labels {
  display: flex;
  gap: var(--space-1);
}

.trend-labels span {
  flex: 1;
  text-align: center;
  font-size: 0.7rem;
  color: var(--text-muted);
}

.opportunities, .warnings {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.opportunities h4 {
  color: #4A9B5A;
  margin-bottom: var(--space-2);
  font-size: 0.95rem;
}

.warnings h4 {
  color: #E85D4C;
  margin-bottom: var(--space-2);
  font-size: 0.95rem;
}

.opportunities ul, .warnings ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.opportunities li, .warnings li {
  padding: var(--space-1) 0;
  padding-left: var(--space-4);
  position: relative;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.opportunities li::before {
  content: "★";
  position: absolute;
  left: 0;
  color: #4A9B5A;
}

.warnings li::before {
  content: "!";
  position: absolute;
  left: 0;
  color: #E85D4C;
}

@media (max-width: 900px) {
  .results-layout {
    grid-template-columns: 1fr;
  }
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

  .category-header {
    flex-wrap: wrap;
  }

  .category-score {
    width: 100%;
    margin-top: var(--space-2);
    text-align: center;
  }

  /* 運勢響應式 */
  .fortune-grid {
    grid-template-columns: 1fr;
  }

  .fortune-item {
    grid-template-columns: auto auto 1fr auto;
  }

  .lucky-grid {
    grid-template-columns: 1fr;
    gap: var(--space-2);
  }

  .weekly-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .trend-chart {
    height: 80px;
  }

  .trend-value {
    font-size: 0.55rem;
  }

  .trend-labels span {
    font-size: 0.6rem;
  }

  .fortune-header {
    flex-direction: column;
  }

  .element-match {
    width: 100%;
    justify-content: center;
  }

  .month-theme {
    align-items: flex-start;
  }

  .year-info {
    flex-wrap: wrap;
  }
}

/* 求職離職指引 */
.career-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.career-content .loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-6);
  color: var(--text-muted);
}

.career-section h4,
.lucky-days-section h4,
.avoid-days-section h4 {
  color: var(--stellar-gold);
  font-size: 1rem;
  margin-bottom: var(--space-3);
}

.career-traits {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: var(--space-4);
}

.career-categories {
  display: grid;
  gap: var(--space-3);
}

.career-category {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.career-category .category-name {
  display: block;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: var(--space-2);
}

.job-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.job-tag {
  padding: var(--space-1) var(--space-2);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.career-advice {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--stellar-gold);
}

.career-advice p {
  color: var(--text-secondary);
  line-height: 1.7;
  font-size: 0.9rem;
}

.lucky-days-list,
.avoid-days-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.lucky-day-item,
.avoid-day-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.lucky-day-item.seeking {
  border-left: 3px solid #4A9B5A;
}

.lucky-day-item.resignation {
  border-left: 3px solid var(--stellar-gold);
}

.avoid-day-item {
  border-left: 3px solid #E85D4C;
}

.day-date {
  font-weight: 500;
  color: var(--text-primary);
  min-width: 120px;
}

.day-score {
  padding: var(--space-1) var(--space-2);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  color: var(--stellar-gold);
}

.day-reason {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.career-content .no-data {
  color: var(--text-muted);
  text-align: center;
  padding: var(--space-4);
}

@media (max-width: 768px) {
  .lucky-day-item,
  .avoid-day-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .day-date {
    min-width: auto;
  }
}
</style>
