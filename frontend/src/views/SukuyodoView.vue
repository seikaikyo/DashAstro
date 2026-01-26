<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProfile } from '../stores/profile'
import CollapsibleCard from '../components/CollapsibleCard.vue'
import MansionWheel from '../components/MansionWheel.vue'

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
  mei: CompatibilityCategory           // 命
  gyotai: CompatibilityCategory        // 業胎
  eishin: CompatibilityCategory        // 榮親
  yusui: CompatibilityCategory         // 友衰
  ankai: CompatibilityCategory         // 安壞
  kisei: CompatibilityCategory         // 危成
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
const date2 = ref('')
const compatibility = ref<CompatibilityResult | null>(null)
const compatLoading = ref(false)
const compatError = ref('')

// 元資料
const metadata = ref<Metadata | null>(null)

// 顯示公式說明
const showFormula = ref(false)

// 顯示歷史典故
const showHistory = ref(false)

// 二十七宿輪盤
interface WheelMansion {
  index: number
  name_jp: string
  name_zh: string
  reading: string
  element: string
  personality?: string
  keywords?: string[]
}
const allMansions = ref<WheelMansion[]>([])
const showWheel = ref(true)
const selectedWheelMansion = ref<WheelMansion | null>(null)

function handleWheelSelect(mansion: WheelMansion) {
  if (selectedWheelMansion.value?.index === mansion.index) {
    selectedWheelMansion.value = null
  } else {
    selectedWheelMansion.value = mansion
  }
}

// 六種關係類型詳解
interface RelationType {
  type: string
  name: string
  name_jp: string
  reading: string
  score: number
  description: string
  detailed: string
  advice: string
  tips: string[]
  avoid: string[]
  good_for: string[]
}
const allRelations = ref<RelationType[]>([])
const showRelations = ref(false)
const expandedRelation = ref<string | null>(null)

function toggleRelation(type: string) {
  expandedRelation.value = expandedRelation.value === type ? null : type
}

// 七曜元素詳解
interface ElementType {
  name: string
  reading: string
  planet: string
  traits: string
  energy: string
}
const allElements = ref<ElementType[]>([])
const showElements = ref(false)

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

// 收藏對象配對
interface PartnerCompatibility {
  partnerId: string
  nickname: string
  birthDate: string
  mansion: {
    name_jp: string
    reading: string
    element: string
  }
  relation: {
    type: string
    name: string
    reading: string
    description: string
  }
  score: number
}
const partnerCompatibilities = ref<PartnerCompatibility[]>([])
const partnerCompatLoading = ref(false)

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

// 六種關係 key 與 CSS 類別對照（依分數由高至低排序）
const relationKeys = [
  { key: 'eishin', cssClass: 'marriage' },     // 榮親 95 分
  { key: 'gyotai', cssClass: 'past-life' },    // 業胎 90 分
  { key: 'mei', cssClass: 'mei' },             // 命 85 分
  { key: 'kisei', cssClass: 'kisei' },         // 危成 75 分
  { key: 'yusui', cssClass: 'yusui' },         // 友衰 70 分
  { key: 'ankai', cssClass: 'avoid' }          // 安壞 50 分
]

// 根據分數回傳顏色類別
function getScoreColorClass(score: number | undefined): string {
  if (!score) return ''
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'normal'
  if (score >= 60) return 'caution'
  return 'warning'
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

  // 載入二十七宿資料
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/mansions`)
    if (res.ok) {
      const data = await res.json()
      if (data.success && data.mansions) {
        allMansions.value = data.mansions
      }
    }
  } catch (e) {
    console.error('Failed to load mansions')
  }

  // 載入六種關係類型
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/relations`)
    if (res.ok) {
      const data = await res.json()
      if (data.relations) {
        allRelations.value = data.relations
      }
    }
  } catch (e) {
    console.error('Failed to load relations')
  }

  // 載入七曜元素
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/elements`)
    if (res.ok) {
      const data = await res.json()
      if (data.elements) {
        allElements.value = data.elements
      }
    }
  } catch (e) {
    console.error('Failed to load elements')
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

// 取得收藏對象配對關係
const fetchPartnerCompatibilities = async () => {
  if (!myBirthDate.value || partnersWithBirthDate.value.length === 0) return

  partnerCompatLoading.value = true
  partnerCompatibilities.value = []

  try {
    const results: PartnerCompatibility[] = []

    for (const partner of partnersWithBirthDate.value) {
      const res = await fetch(`${apiUrl}/api/sukuyodo/compatibility`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date1: myBirthDate.value,
          date2: partner.birthDate
        })
      })

      if (res.ok) {
        const data = await res.json()
        if (data.success) {
          const compat = data.data as CompatibilityResult
          results.push({
            partnerId: partner.id,
            nickname: partner.nickname,
            birthDate: partner.birthDate!,
            mansion: {
              name_jp: compat.person2.mansion,
              reading: compat.person2.reading,
              element: compat.person2.element
            },
            relation: {
              type: compat.relation.type,
              name: compat.relation.name,
              reading: compat.relation.reading,
              description: compat.relation.description
            },
            score: compat.score
          })
        }
      }
    }

    // 依分數由高到低排序
    partnerCompatibilities.value = results.sort((a, b) => b.score - a.score)
  } catch (e) {
    console.error('Failed to fetch partner compatibilities')
  } finally {
    partnerCompatLoading.value = false
  }
}

const getFortuneLevel = (score: number) => {
  if (score >= 90) return { text: '大吉', class: 'excellent' }
  if (score >= 75) return { text: '吉', class: 'good' }
  if (score >= 60) return { text: '中吉', class: 'fair' }
  if (score >= 45) return { text: '小吉', class: 'caution' }
  return { text: '凶', class: 'warning' }
}

const getScoreClass = (score: number) => {
  if (score >= 90) return 'excellent'
  if (score >= 75) return 'good'
  if (score >= 60) return 'fair'
  if (score >= 45) return 'caution'
  return 'warning'
}

const calculateCompatibility = async () => {
  if (!myBirthDate.value || !date2.value) return

  compatLoading.value = true
  compatError.value = ''
  compatibility.value = null

  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/compatibility`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        date1: myBirthDate.value,
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
            name="sukuyodo-birthdate"
            v-model="birthDate"
            label="西曆生日"
            :max="new Date().toISOString().split('T')[0]"
          ></sl-input>
          <button
            class="btn-gold"
            @click="lookupMansion"
            :disabled="!birthDate || lookupLoading"
            :aria-busy="lookupLoading"
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
              <!-- 六種關係類型 -->
              <div
                v-for="relKey in relationKeys"
                :key="relKey.key"
                class="finder-category"
                :class="relKey.cssClass"
              >
                <div class="category-header">
                  <ruby class="category-name">
                    {{ compatFinder[relKey.key as keyof CompatibilityFinderResult]?.relation }}<rp>(</rp><rt>{{ (compatFinder[relKey.key as keyof CompatibilityFinderResult] as CompatibilityCategory)?.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="category-score" :class="getScoreColorClass((compatFinder[relKey.key as keyof CompatibilityFinderResult] as CompatibilityCategory)?.score)">
                    {{ (compatFinder[relKey.key as keyof CompatibilityFinderResult] as CompatibilityCategory)?.score }} 分
                  </span>
                </div>
                <p class="category-desc">{{ (compatFinder[relKey.key as keyof CompatibilityFinderResult] as CompatibilityCategory)?.description }}</p>
                <div class="mansion-grid">
                  <button
                    v-for="m in (compatFinder[relKey.key as keyof CompatibilityFinderResult] as CompatibilityCategory)?.mansions"
                    :key="m.index"
                    class="mansion-chip"
                    :class="{ active: selectedMansion?.index === m.index, danger: relKey.key === 'ankai' }"
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
          title="與對方的相性"
          subtitle="輸入對方生日，分析你們的緣分"
          icon="heart"
          :badge="compatibility ? `${compatibility.score} ${getScoreLevel(compatibility.score).text}` : undefined"
          :badge-class="compatibility ? getScoreLevel(compatibility.score).class : ''"
          :default-open="false"
        >
          <div class="compat-content">
            <!-- 未設定自己生日 -->
            <div v-if="!myBirthDate" class="compat-no-birth">
              <sl-icon name="exclamation-circle"></sl-icon>
              <p>請先設定你的生日才能進行相性診斷</p>
              <router-link to="/profile" class="link-btn">前往設定</router-link>
            </div>

            <template v-else>
              <div class="compat-form">
                <!-- 顯示自己的本命宿 -->
                <div class="my-mansion-display" v-if="mansion">
                  <span class="label">你的本命宿</span>
                  <ruby class="mansion-name">
                    {{ mansion.name_jp }}<rp>(</rp><rt>{{ mansion.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="mansion-element" :style="{ color: elementColors[mansion.element] }">（{{ mansion.element }}）</span>
                </div>

                <div class="form-group">
                  <sl-input
                    type="date"
                    name="compat-person2-birthdate"
                    v-model="date2"
                    label="對方的生日"
                    :max="new Date().toISOString().split('T')[0]"
                  ></sl-input>
                </div>
                <button
                  class="btn-gold"
                  @click="calculateCompatibility"
                  :disabled="!date2 || compatLoading"
                  :aria-busy="compatLoading"
                >
                  <sl-spinner v-if="compatLoading"></sl-spinner>
                  <span v-else>分析相性</span>
                </button>
              </div>
            </template>

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

        <!-- 我的配對關係 -->
        <CollapsibleCard
          title="我的配對關係"
          subtitle="一鍵查看你與收藏對象的宿曜相性"
          icon="people-fill"
          :default-open="false"
          @toggle="(open: boolean) => { if (open && partnerCompatibilities.length === 0) fetchPartnerCompatibilities() }"
        >
          <div class="partner-compat-content">
            <!-- 未設定自己生日 -->
            <div v-if="!myBirthDate" class="empty-state">
              <sl-icon name="calendar-x"></sl-icon>
              <p>請先設定你的生日</p>
              <router-link to="/profile" class="link-btn">前往設定</router-link>
            </div>

            <!-- 無收藏對象 -->
            <div v-else-if="partnersWithBirthDate.length === 0" class="empty-state">
              <sl-icon name="person-plus"></sl-icon>
              <p>你還沒有設定有生日的關注對象</p>
              <router-link to="/profile" class="link-btn">新增關注對象</router-link>
            </div>

            <!-- 載入中 -->
            <div v-else-if="partnerCompatLoading" class="loading-state">
              <sl-spinner></sl-spinner>
              <span>計算配對中...</span>
            </div>

            <!-- 配對結果 -->
            <template v-else-if="partnerCompatibilities.length > 0">
              <div
                v-for="pc in partnerCompatibilities"
                :key="pc.partnerId"
                class="partner-compat-card"
              >
                <div class="pc-header">
                  <span class="pc-nickname">{{ pc.nickname }}</span>
                  <span class="pc-score" :class="getScoreColorClass(pc.score)">{{ pc.score }} 分</span>
                </div>
                <div class="pc-mansion">
                  <span>生日 {{ pc.birthDate }}</span>
                  <span class="pc-arrow">→</span>
                  <ruby>
                    {{ pc.mansion.name_jp }}<rp>(</rp><rt>{{ pc.mansion.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="pc-element" :style="{ color: elementColors[pc.mansion.element] }">（{{ pc.mansion.element }}）</span>
                </div>
                <div class="pc-relation">
                  <span class="pc-relation-label">與你的關係：</span>
                  <ruby class="pc-relation-name">
                    {{ pc.relation.name }}<rp>(</rp><rt>{{ pc.relation.reading }}</rt><rp>)</rp>
                  </ruby>
                </div>
                <p class="pc-desc">{{ pc.relation.description }}</p>

                <!-- 分數條 -->
                <div class="pc-score-bar">
                  <div class="bar-fill" :style="{ width: pc.score + '%' }" :class="getScoreColorClass(pc.score)"></div>
                </div>
              </div>

              <router-link to="/profile" class="add-partner-link">
                <sl-icon name="plus-circle"></sl-icon>
                新增關注對象
              </router-link>
            </template>

            <!-- 尚未載入 -->
            <div v-else class="empty-state">
              <sl-icon name="arrow-clockwise"></sl-icon>
              <p>展開此卡片以載入配對資料</p>
            </div>
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

      <!-- 二十七宿輪盤 -->
      <section v-if="allMansions.length > 0" class="wheel-section card">
        <button class="wheel-toggle" @click="showWheel = !showWheel">
          <h2><ruby>二十七宿<rp>(</rp><rt>にじゅうしちしゅく</rt><rp>)</rp></ruby>輪盤</h2>
          <sl-icon :name="showWheel ? 'chevron-up' : 'chevron-down'"></sl-icon>
        </button>

        <div v-if="showWheel" class="wheel-content">
          <p class="wheel-intro">
            二十七宿依據四方神獸分為四象：東方青龍七宿（角至箕）、北方玄武七宿（斗至壁）、
            西方白虎七宿（奎至參）、南方朱雀六宿（井至軫）。點擊任意星宿可查看詳細資訊。
          </p>

          <MansionWheel
            :mansions="allMansions"
            :user-mansion-index="mansion?.index ?? null"
            :highlighted-indices="compatFinder ? [
              ...compatFinder.eishin.mansions.map(m => m.index),
              ...compatFinder.gyotai.mansions.map(m => m.index),
              ...compatFinder.mei.mansions.map(m => m.index)
            ] : []"
            @select="handleWheelSelect"
          />

          <div v-if="selectedWheelMansion" class="wheel-detail">
            <div class="detail-header">
              <ruby class="detail-name">
                {{ selectedWheelMansion.name_jp }}<rp>(</rp><rt>{{ selectedWheelMansion.reading }}</rt><rp>)</rp>
              </ruby>
              <span
                class="detail-element"
                :style="{ borderColor: elementColors[selectedWheelMansion.element], color: elementColors[selectedWheelMansion.element] }"
              >
                {{ selectedWheelMansion.element }}
              </span>
            </div>
            <p v-if="selectedWheelMansion.personality" class="detail-desc">
              {{ selectedWheelMansion.personality }}
            </p>
            <div v-if="selectedWheelMansion.keywords?.length" class="detail-keywords">
              <span v-for="kw in selectedWheelMansion.keywords" :key="kw" class="keyword-tag">{{ kw }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 六種關係詳解 -->
      <section v-if="allRelations.length > 0" class="relations-section card">
        <button class="relations-toggle" @click="showRelations = !showRelations">
          <h2><ruby>六種關係<rp>(</rp><rt>ろくしゅかんけい</rt><rp>)</rp></ruby>詳解</h2>
          <sl-icon :name="showRelations ? 'chevron-up' : 'chevron-down'"></sl-icon>
        </button>

        <div v-if="showRelations" class="relations-content">
          <p class="relations-intro">
            宿曜道以「三九秘法」將人際關係分為六種類型。點擊任一關係可展開詳細說明，
            包含建議、適合場景以及需要注意的事項。
          </p>

          <div class="relation-cards">
            <div
              v-for="rel in allRelations"
              :key="rel.type"
              class="relation-card"
              :class="{ expanded: expandedRelation === rel.type }"
            >
              <button class="relation-header" @click="toggleRelation(rel.type)">
                <div class="relation-title">
                  <ruby class="rel-name-large">
                    {{ rel.name_jp }}<rp>(</rp><rt>{{ rel.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="rel-score" :class="getScoreClass(rel.score)">{{ rel.score }}分</span>
                </div>
                <p class="rel-desc-brief">{{ rel.description }}</p>
                <sl-icon :name="expandedRelation === rel.type ? 'chevron-up' : 'chevron-down'" class="expand-icon"></sl-icon>
              </button>

              <div v-if="expandedRelation === rel.type" class="relation-details">
                <div class="detail-block detailed">
                  <h4>詳細說明</h4>
                  <p>{{ rel.detailed }}</p>
                </div>

                <div class="detail-block advice">
                  <h4>經營建議</h4>
                  <p>{{ rel.advice }}</p>
                </div>

                <div v-if="rel.tips?.length" class="detail-block tips">
                  <h4>具體做法</h4>
                  <ul>
                    <li v-for="tip in rel.tips" :key="tip">{{ tip }}</li>
                  </ul>
                </div>

                <div v-if="rel.avoid?.length" class="detail-block avoid">
                  <h4>需要避免</h4>
                  <ul>
                    <li v-for="item in rel.avoid" :key="item">{{ item }}</li>
                  </ul>
                </div>

                <div v-if="rel.good_for?.length" class="detail-block good-for">
                  <h4>適合場景</h4>
                  <div class="tags">
                    <span v-for="item in rel.good_for" :key="item" class="tag">{{ item }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 七曜元素詳解 -->
      <section v-if="allElements.length > 0" class="elements-section card">
        <button class="elements-toggle" @click="showElements = !showElements">
          <h2><ruby>七曜<rp>(</rp><rt>しちよう</rt><rp>)</rp></ruby>元素詳解</h2>
          <sl-icon :name="showElements ? 'chevron-up' : 'chevron-down'"></sl-icon>
        </button>

        <div v-if="showElements" class="elements-content">
          <p class="elements-intro">
            七曜（日、月、火、水、木、金、土）對應一週七天，每種元素具有獨特的能量特質。
            了解你的本命宿元素，能更好地把握每日運勢的起伏。
          </p>

          <div class="element-cards">
            <div
              v-for="elem in allElements"
              :key="elem.name"
              class="element-card"
              :style="{ borderColor: elementColors[elem.name] }"
            >
              <div class="element-header">
                <span class="element-name" :style="{ color: elementColors[elem.name] }">
                  {{ elem.name }}
                </span>
                <ruby class="element-reading">
                  {{ elem.planet }}<rp>(</rp><rt>{{ elem.reading }}</rt><rp>)</rp>
                </ruby>
                <span class="element-energy" :class="elem.energy === '陽' ? 'yang' : elem.energy === '陰' ? 'yin' : 'neutral'">
                  {{ elem.energy }}
                </span>
              </div>
              <p class="element-traits">{{ elem.traits }}</p>
            </div>
          </div>

          <div class="element-cycle-section">
            <h4>五行相生相剋</h4>
            <div class="cycle-diagram">
              <div class="cycle-row">
                <span class="cycle-label">相生：</span>
                <span class="cycle-flow">
                  <span :style="{ color: elementColors['木'] }">木</span> →
                  <span :style="{ color: elementColors['火'] }">火</span> →
                  <span :style="{ color: elementColors['土'] }">土</span> →
                  <span :style="{ color: elementColors['金'] }">金</span> →
                  <span :style="{ color: elementColors['水'] }">水</span> →
                  <span :style="{ color: elementColors['木'] }">木</span>
                </span>
              </div>
              <div class="cycle-row">
                <span class="cycle-label">相剋：</span>
                <span class="cycle-flow">
                  <span :style="{ color: elementColors['木'] }">木</span> ⊗
                  <span :style="{ color: elementColors['土'] }">土</span> ⊗
                  <span :style="{ color: elementColors['水'] }">水</span> ⊗
                  <span :style="{ color: elementColors['火'] }">火</span> ⊗
                  <span :style="{ color: elementColors['金'] }">金</span> ⊗
                  <span :style="{ color: elementColors['木'] }">木</span>
                </span>
              </div>
            </div>
            <p class="cycle-note">
              日、月為特殊元素：太陽為至陽之體，能生助火性；月亮為至陰之體，能生助水性。
            </p>
          </div>
        </div>
      </section>

      <!-- 關於宿曜道 - 詳細歷史介紹 -->
      <section class="history-section card">
        <button class="history-toggle" @click="showHistory = !showHistory">
          <h2>關於<ruby>宿曜道<rp>(</rp><rt>しゅくようどう</rt><rp>)</rp></ruby></h2>
          <sl-icon :name="showHistory ? 'chevron-up' : 'chevron-down'"></sl-icon>
        </button>

        <div v-if="showHistory" class="history-content">
          <!-- 起源 -->
          <div class="history-block">
            <h3>起源</h3>
            <p>
              宿曜道源自古印度的「<ruby>納沙特拉<rp>(</rp><rt>Nakshatra</rt><rp>)</rp></ruby>」占星術，
              是印度最古老的天文體系之一。此法將黃道周天分為 27 個區域，稱為「<ruby>二十七宿<rp>(</rp><rt>にじゅうしちしゅく</rt><rp>)</rp></ruby>」，
              每個星宿對應約 13 度又 20 分的天區。
            </p>
            <p>
              這套體系經由絲路傳入中國，於唐代與中國本土天文學融合，成為兼具印度和中華特色的占星系統。
              《宿曜經》記載的推算方法，至今仍是研究東亞占星術的重要文獻。
            </p>
          </div>

          <!-- 傳入日本 -->
          <div class="history-block">
            <h3>傳入日本</h3>
            <p>
              <ruby>延曆<rp>(</rp><rt>えんりゃく</rt><rp>)</rp></ruby>23 年（西元 804 年），
              <ruby>空海<rp>(</rp><rt>くうかい</rt><rp>)</rp></ruby>大師入唐求法，於長安
              <ruby>青龍寺<rp>(</rp><rt>せいりゅうじ</rt><rp>)</rp></ruby>師從
              <ruby>惠果<rp>(</rp><rt>けいか</rt><rp>)</rp></ruby>阿闍梨，習得<ruby>真言密教<rp>(</rp><rt>しんごんみっきょう</rt><rp>)</rp></ruby>。
            </p>
            <p>
              空海歸國時攜回大量經典，其中包括《<ruby>宿曜經<rp>(</rp><rt>すくようきょう</rt><rp>)</rp></ruby>》
              （全名《文殊師利菩薩及諸仙所說吉凶時日善惡宿曜經》）。
              這部經典系統地闡述了二十七宿的性質、吉凶判斷、以及人際關係推算的方法，
              成為日本宿曜道的根本經典。
            </p>
          </div>

          <!-- 三九秘法 -->
          <div class="history-block">
            <h3><ruby>三九秘法<rp>(</rp><rt>さんくひほう</rt><rp>)</rp></ruby></h3>
            <p>
              宿曜道以「三九秘法」計算人際關係。此法根據兩人本命宿在二十七宿輪盤上的距離，
              判定六種基本關係類型：
            </p>
            <div class="relation-intro-grid">
              <div class="relation-intro-item">
                <ruby class="rel-title">命<rp>(</rp><rt>めい</rt><rp>)</rp></ruby>
                <span class="rel-brief">距離 0 宿，如同鏡子般的存在，彼此理解但優缺點皆被放大</span>
              </div>
              <div class="relation-intro-item">
                <ruby class="rel-title">業胎<rp>(</rp><rt>ぎょうたい</rt><rp>)</rp></ruby>
                <span class="rel-brief">距離 9 或 18 宿，前世因緣深厚，常有似曾相識之感</span>
              </div>
              <div class="relation-intro-item">
                <ruby class="rel-title">栄親<rp>(</rp><rt>えいしん</rt><rp>)</rp></ruby>
                <span class="rel-brief">互相提攜成長的良緣，傳統上被視為最佳結合</span>
              </div>
              <div class="relation-intro-item">
                <ruby class="rel-title">友衰<rp>(</rp><rt>ゆうすい</rt><rp>)</rp></ruby>
                <span class="rel-brief">相處舒適自在，但需注意不要一起停滯不前</span>
              </div>
              <div class="relation-intro-item">
                <ruby class="rel-title">安壊<rp>(</rp><rt>あんかい</rt><rp>)</rp></ruby>
                <span class="rel-brief">一方安定一方破壞，權力不對等需謹慎經營</span>
              </div>
              <div class="relation-intro-item">
                <ruby class="rel-title">危成<rp>(</rp><rt>きせい</rt><rp>)</rp></ruby>
                <span class="rel-brief">互補的關係，需要磨合但能促進彼此成長</span>
              </div>
            </div>
          </div>

          <!-- 現代應用 -->
          <div class="history-block">
            <h3>現代應用</h3>
            <p>
              時至今日，日本仍廣泛使用宿曜道於婚配、擇日、人事安排等領域。
              許多企業主管會參考員工的本命宿來組建團隊，以達到人盡其才、互補協作的效果。
            </p>
            <p>
              宿曜道的價值不在於預測命運，而在於提供理解人際關係的框架。
              透過認識不同的關係類型，我們能更有智慧地經營與他人的互動，
              在相處中取長補短、互相成長。
            </p>
          </div>

          <!-- 七曜說明 -->
          <div class="history-block">
            <h3><ruby>七曜<rp>(</rp><rt>しちよう</rt><rp>)</rp></ruby>與運勢</h3>
            <p>
              宿曜道同時納入七曜（日、月、火、水、木、金、土）的概念，
              這正是現代一週七天名稱的由來。每一天由不同的行星主宰，
              結合個人本命宿的五行屬性，產生獨特的運勢變化。
            </p>
            <div class="element-info-grid">
              <div class="element-info-item"><span class="elem-badge elem-sun">日</span>太陽主宰，能量充沛，利於領導和決策</div>
              <div class="element-info-item"><span class="elem-badge elem-moon">月</span>月亮主宰，直覺敏銳，適合創意和情感交流</div>
              <div class="element-info-item"><span class="elem-badge elem-fire">火</span>火星主宰，行動力強，適合挑戰和競爭</div>
              <div class="element-info-item"><span class="elem-badge elem-water">水</span>水星主宰，思維靈活，適合溝通和學習</div>
              <div class="element-info-item"><span class="elem-badge elem-wood">木</span>木星主宰，擴展成長，適合規劃和發展</div>
              <div class="element-info-item"><span class="elem-badge elem-metal">金</span>金星主宰，和諧收斂，適合社交和藝術</div>
              <div class="element-info-item"><span class="elem-badge elem-earth">土</span>土星主宰，穩定踏實，適合鞏固和累積</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 簡介區塊（折疊狀態的預覽） -->
      <section v-if="!showHistory" class="intro-section">
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

.compat-no-birth {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6);
  text-align: center;
  color: var(--text-muted);
}

.compat-no-birth sl-icon {
  font-size: 2rem;
  color: var(--border-default);
}

.compat-no-birth p {
  margin: 0;
}

.compat-no-birth .link-btn {
  display: inline-flex;
  padding: var(--space-2) var(--space-4);
  background: var(--stellar-gold);
  color: var(--cosmos-night);
  border-radius: var(--radius-md);
  text-decoration: none;
  font-weight: 500;
}

.my-mansion-display {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-2);
}

.my-mansion-display .label {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.my-mansion-display .mansion-name {
  font-weight: 600;
  color: var(--stellar-gold);
}

.my-mansion-display .mansion-name rt {
  font-size: 0.6em;
}

.my-mansion-display .mansion-element {
  font-weight: 500;
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
  color: #4A9B5A;  /* 榮親 - 綠色 */
}

.finder-category.past-life .category-name {
  color: #9B7FCF;  /* 業胎 - 紫色 */
}

.finder-category.mei .category-name {
  color: #7CB3D9;  /* 命 - 藍色 */
}

.finder-category.kisei .category-name {
  color: #E89B3C;  /* 危成 - 橙色 */
}

.finder-category.yusui .category-name {
  color: #8B7355;  /* 友衰 - 褐色 */
}

.finder-category.avoid .category-name {
  color: #E85D4C;  /* 安壞 - 紅色 */
}

.category-score {
  margin-left: auto;
  padding: var(--space-1) var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  color: var(--stellar-gold);
}

.category-score.excellent {
  color: #4A9B5A;  /* 90+ 分 */
}

.category-score.good {
  color: #7CB3D9;  /* 80-89 分 */
}

.category-score.normal {
  color: #8B7355;  /* 70-79 分 */
}

.category-score.caution {
  color: #E89B3C;  /* 60-69 分 */
}

.category-score.warning {
  color: #E85D4C;  /* 60 分以下 */
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

/* 我的配對關係 */
.partner-compat-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.partner-compat-content .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-8);
  text-align: center;
  color: var(--text-muted);
}

.partner-compat-content .empty-state sl-icon {
  font-size: 2.5rem;
  color: var(--border-default);
}

.partner-compat-content .empty-state p {
  margin: 0;
}

.partner-compat-content .link-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--stellar-gold);
  color: var(--cosmos-night);
  border-radius: var(--radius-md);
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}

.partner-compat-content .link-btn:hover {
  opacity: 0.9;
}

.partner-compat-content .loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-6);
  color: var(--text-secondary);
}

.partner-compat-card {
  background: var(--cosmos-twilight);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.pc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.pc-nickname {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--stellar-gold);
}

.pc-score {
  font-weight: 600;
  padding: var(--space-1) var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-full);
}

.pc-score.excellent { color: #4A9B5A; }
.pc-score.good { color: #7CB3D9; }
.pc-score.normal { color: #8B7355; }
.pc-score.caution { color: #E89B3C; }
.pc-score.warning { color: #E85D4C; }

.pc-mansion {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.pc-arrow {
  color: var(--text-muted);
}

.pc-element {
  font-weight: 500;
}

.pc-relation {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.pc-relation-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.pc-relation-name {
  font-weight: 600;
  color: var(--text-primary);
}

.pc-relation-name rt {
  font-size: 0.6em;
}

.pc-desc {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0 0 var(--space-3);
  line-height: 1.5;
}

.pc-score-bar {
  height: 6px;
  background: var(--cosmos-night);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.pc-score-bar .bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.pc-score-bar .bar-fill.excellent { background: #4A9B5A; }
.pc-score-bar .bar-fill.good { background: #7CB3D9; }
.pc-score-bar .bar-fill.normal { background: #8B7355; }
.pc-score-bar .bar-fill.caution { background: #E89B3C; }
.pc-score-bar .bar-fill.warning { background: #E85D4C; }

.add-partner-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3);
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  text-decoration: none;
  transition: all 0.2s;
}

.add-partner-link:hover {
  border-color: var(--stellar-gold);
  color: var(--stellar-gold);
}

/* 二十七宿輪盤 */
.wheel-section {
  max-width: 700px;
  margin: 0 auto var(--space-12);
}

.wheel-toggle {
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

.wheel-toggle h2 {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.wheel-toggle sl-icon {
  color: var(--text-muted);
}

.wheel-content {
  margin-top: var(--space-6);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-6);
}

.wheel-intro {
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.7;
  max-width: 500px;
}

.wheel-detail {
  width: 100%;
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  border: 1px solid var(--stellar-gold);
}

.wheel-detail .detail-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.wheel-detail .detail-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--stellar-gold);
}

.wheel-detail .detail-name rt {
  font-size: 0.5em;
}

.wheel-detail .detail-element {
  padding: var(--space-1) var(--space-3);
  border: 1px solid;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.wheel-detail .detail-desc {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.7;
  margin-bottom: var(--space-3);
}

.wheel-detail .detail-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

/* 六種關係詳解 */
.relations-section {
  max-width: 800px;
  margin: 0 auto var(--space-12);
}

.relations-toggle {
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

.relations-toggle h2 {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.relations-toggle sl-icon {
  color: var(--text-muted);
}

.relations-content {
  margin-top: var(--space-6);
}

.relations-intro {
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.7;
  margin-bottom: var(--space-6);
}

.relation-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.relation-card {
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: all 0.2s ease;
}

.relation-card.expanded {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.relation-header {
  width: 100%;
  padding: var(--space-4);
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  color: inherit;
  position: relative;
}

.relation-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.rel-name-large {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--stellar-gold);
}

.rel-name-large rt {
  font-size: 0.5em;
}

.rel-score {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 600;
}

.rel-score.excellent { background: rgba(74, 155, 90, 0.2); color: #4A9B5A; }
.rel-score.good { background: rgba(199, 163, 101, 0.2); color: var(--stellar-gold); }
.rel-score.fair { background: rgba(124, 179, 217, 0.2); color: #7CB3D9; }
.rel-score.caution { background: rgba(232, 155, 60, 0.2); color: #E89B3C; }
.rel-score.warning { background: rgba(232, 93, 76, 0.2); color: #E85D4C; }

.rel-desc-brief {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
  padding-right: var(--space-8);
}

.expand-icon {
  position: absolute;
  right: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.relation-details {
  padding: 0 var(--space-4) var(--space-4);
  display: grid;
  gap: var(--space-4);
  border-top: 1px solid var(--border-default);
  margin-top: var(--space-2);
  padding-top: var(--space-4);
}

.relation-details .detail-block {
  padding: var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.relation-details .detail-block h4 {
  color: var(--stellar-gold);
  font-size: 0.9rem;
  margin-bottom: var(--space-2);
}

.relation-details .detail-block p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.7;
  margin: 0;
}

.relation-details .detail-block ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.relation-details .detail-block ul li {
  padding: var(--space-1) 0;
  padding-left: var(--space-4);
  position: relative;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.relation-details .tips ul li::before {
  content: "○";
  position: absolute;
  left: 0;
  color: #4A9B5A;
}

.relation-details .avoid ul li::before {
  content: "✕";
  position: absolute;
  left: 0;
  color: #E85D4C;
}

.relation-details .tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

/* 七曜元素詳解 */
.elements-section {
  max-width: 800px;
  margin: 0 auto var(--space-12);
}

.elements-toggle {
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

.elements-toggle h2 {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.elements-toggle sl-icon {
  color: var(--text-muted);
}

.elements-content {
  margin-top: var(--space-6);
}

.elements-intro {
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.7;
  margin-bottom: var(--space-6);
}

.element-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.element-card {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  border-left: 3px solid;
}

.element-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
  flex-wrap: wrap;
}

.element-name {
  font-size: 1.3rem;
  font-weight: 700;
}

.element-reading {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.element-reading rt {
  font-size: 0.6em;
}

.element-energy {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  margin-left: auto;
}

.element-energy.yang {
  background: rgba(232, 155, 60, 0.2);
  color: #E89B3C;
}

.element-energy.yin {
  background: rgba(124, 179, 217, 0.2);
  color: #7CB3D9;
}

.element-energy.neutral {
  background: rgba(139, 115, 85, 0.2);
  color: #8B7355;
}

.element-traits {
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.6;
  margin: 0;
}

.element-cycle-section {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.element-cycle-section h4 {
  color: var(--stellar-gold);
  font-size: 0.95rem;
  margin-bottom: var(--space-3);
  text-align: center;
}

.cycle-diagram {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.cycle-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  justify-content: center;
  flex-wrap: wrap;
}

.cycle-label {
  color: var(--text-muted);
  font-size: 0.85rem;
  min-width: 50px;
}

.cycle-flow {
  font-size: 0.95rem;
  font-weight: 500;
}

.cycle-flow span {
  font-weight: 600;
}

.cycle-note {
  color: var(--text-muted);
  font-size: 0.85rem;
  text-align: center;
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 600px) {
  .element-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .relation-details {
    grid-template-columns: 1fr;
  }
}

/* 宿曜道典故區塊 */
.history-section {
  max-width: 700px;
  margin: 0 auto var(--space-12);
}

.history-toggle {
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

.history-toggle h2 {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.history-toggle sl-icon {
  color: var(--text-muted);
}

.history-content {
  margin-top: var(--space-6);
  display: grid;
  gap: var(--space-6);
}

.history-block {
  padding: var(--space-6);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.history-block h3 {
  color: var(--stellar-gold);
  margin-bottom: var(--space-4);
  font-size: 1rem;
}

.history-block p {
  color: var(--text-secondary);
  line-height: 1.8;
  font-size: 0.9rem;
  margin-bottom: var(--space-3);
}

.history-block p:last-child {
  margin-bottom: 0;
}

.history-block ruby rt {
  font-size: 0.6em;
}

/* 六種關係簡介 */
.relation-intro-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.relation-intro-item {
  padding: var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.rel-title {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}

.rel-title strong {
  color: var(--stellar-gold);
  font-size: 0.95rem;
}

.rel-title span {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.rel-brief {
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.5;
}

/* 七曜元素說明 */
.element-info-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.element-info-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.elem-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: 600;
}

.elem-badge.sun { background: #E89B3C; color: #1a1a2e; }
.elem-badge.moon { background: #C0C0C0; color: #1a1a2e; }
.elem-badge.fire { background: #E85D4C; color: #fff; }
.elem-badge.water { background: #2D3436; color: #fff; border: 1px solid var(--border-default); }
.elem-badge.wood { background: #4A9B5A; color: #fff; }
.elem-badge.gold { background: #F5F5F5; color: #1a1a2e; }
.elem-badge.earth { background: #C4A052; color: #1a1a2e; }

.elem-info {
  display: flex;
  flex-direction: column;
}

.elem-info strong {
  color: var(--text-primary);
  font-size: 0.85rem;
}

.elem-info span {
  color: var(--text-muted);
  font-size: 0.75rem;
}

/* 響應式調整 */
@media (max-width: 600px) {
  .relation-intro-grid {
    grid-template-columns: 1fr;
  }

  .element-info-grid {
    justify-content: center;
  }
}
</style>
