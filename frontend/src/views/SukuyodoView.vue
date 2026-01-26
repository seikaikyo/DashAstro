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

// Tab 導航狀態
const activeMainTab = ref<'fortune' | 'match' | 'lucky' | 'knowledge'>('fortune')
const activeFortuneTab = ref<'daily' | 'weekly' | 'monthly' | 'yearly'>('daily')
const activeMatchTab = ref<'finder' | 'compat' | 'partners'>('finder')
const showQueryInput = ref(false)  // 展開式查詢輸入區

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

// 吉日查詢
interface LuckyDayAction {
  key: string
  name: string
}
interface LuckyDayCategory {
  key: string
  name: string
  icon: string
  actions: LuckyDayAction[]
}
interface LuckyDay {
  date: string
  weekday: string
  score: number
  rating?: string
  reason: string
}
interface LuckyDayResult {
  category: string
  category_name: string
  action: string
  action_name: string
  your_mansion: {
    name_jp: string
    reading: string
    element: string
  }
  lucky_days: LuckyDay[]
  avoid_days: LuckyDay[]
  advice: string
}
const luckyDayCategories = ref<LuckyDayCategory[]>([])
const selectedLuckyCategory = ref<string | null>(null)
const selectedLuckyAction = ref<string | null>(null)
const luckyDayResult = ref<LuckyDayResult | null>(null)
const luckyDayLoading = ref(false)

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

  // 載入吉日查詢類別
  fetchLuckyDayCategories()
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
  luckyDayResult.value = null

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
    fetchYearlyFortune()
  ])
}

// 載入吉日查詢類別
const fetchLuckyDayCategories = async () => {
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/lucky-days/categories`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        luckyDayCategories.value = data.categories
      }
    }
  } catch (e) {
    console.error('Failed to fetch lucky day categories')
  }
}

// 查詢吉日
const fetchLuckyDays = async () => {
  if (!myBirthDate.value || !selectedLuckyCategory.value || !selectedLuckyAction.value) return

  luckyDayLoading.value = true
  luckyDayResult.value = null

  try {
    const res = await fetch(
      `${apiUrl}/api/sukuyodo/lucky-days/${myBirthDate.value}?category=${selectedLuckyCategory.value}&action=${selectedLuckyAction.value}`
    )
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        luckyDayResult.value = data.data
      }
    }
  } catch (e) {
    console.error('Failed to fetch lucky days')
  } finally {
    luckyDayLoading.value = false
  }
}

// 選擇類別時重置項目
const selectLuckyCategory = (categoryKey: string) => {
  selectedLuckyCategory.value = categoryKey
  selectedLuckyAction.value = null
  luckyDayResult.value = null
}

// 選擇項目後自動查詢
const selectLuckyAction = (actionKey: string) => {
  selectedLuckyAction.value = actionKey
  fetchLuckyDays()
}

// 取得當前類別的項目列表
const currentCategoryActions = computed(() => {
  if (!selectedLuckyCategory.value) return []
  const cat = luckyDayCategories.value.find(c => c.key === selectedLuckyCategory.value)
  return cat?.actions || []
})

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

// 當日宿關係類型的樣式類別
const getMansionRelationClass = (relationType: string) => {
  // 使用羅馬拼音 key，與 API 回傳的 mansion_relation.type 一致
  const classMap: Record<string, string> = {
    'eishin': 'relation-excellent',  // 榮親 - 大吉
    'gyotai': 'relation-good',       // 業胎 - 吉
    'mei': 'relation-fair',          // 命 - 中吉
    'yusui': 'relation-neutral',     // 友衰 - 中吉偏低
    'kisei': 'relation-caution',     // 危成 - 小吉
    'ankai': 'relation-warning'      // 安壞 - 凶
  }
  return classMap[relationType] || 'relation-neutral'
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
      <!-- 頂部標題列 -->
      <header class="page-header-bar">
        <h1>
          <ruby>宿曜道<rp>(</rp><rt>しゅくようどう</rt><rp>)</rp></ruby>
        </h1>
        <button
          class="query-toggle-btn"
          :class="{ active: showQueryInput }"
          @click="showQueryInput = !showQueryInput"
        >
          <sl-icon :name="showQueryInput ? 'x-lg' : 'search'"></sl-icon>
          <span>{{ showQueryInput ? '收起' : '查詢本命宿' }}</span>
        </button>
      </header>

      <!-- 展開式查詢區域 -->
      <section v-if="showQueryInput" class="lookup-form-expanded card card-gold">
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
            @click="birthDate = myBirthDate; lookupMansion(); showQueryInput = false"
          >
            我
          </button>
          <button
            v-for="partner in partnersWithBirthDate"
            :key="partner.id"
            class="quick-select-btn"
            :class="{ active: birthDate === partner.birthDate }"
            @click="birthDate = partner.birthDate!; lookupMansion(); showQueryInput = false"
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
            @click="lookupMansion(); showQueryInput = false"
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

      <!-- 摘要卡：本命宿 + 今日運勢 -->
      <section v-if="mansion" class="summary-card">
        <div class="summary-left">
          <ruby class="summary-mansion">
            {{ mansion.name_jp }}<rp>(</rp><rt>{{ mansion.reading }}</rt><rp>)</rp>
          </ruby>
          <span class="summary-element" :style="{ color: mansionElementColor }">{{ mansion.element }}</span>
        </div>
        <div v-if="dailyFortune" class="summary-right">
          <span class="summary-score" :class="getFortuneLevel(dailyFortune.fortune.overall).class">
            {{ dailyFortune.fortune.overall }}
          </span>
          <span class="summary-label">今日運勢</span>
        </div>
        <div v-else class="summary-right loading">
          <sl-spinner></sl-spinner>
        </div>
      </section>

      <!-- 未查詢時的引導 -->
      <section v-if="!mansion && !showQueryInput" class="empty-guide card">
        <sl-icon name="stars"></sl-icon>
        <h2>探索你的本命宿</h2>
        <p>點擊右上角「查詢本命宿」開始</p>
        <button class="btn-gold" @click="showQueryInput = true">開始查詢</button>
      </section>

      <!-- 主要 Tab 導航 -->
      <nav v-if="mansion" class="main-tabs">
        <button
          class="main-tab"
          :class="{ active: activeMainTab === 'fortune' }"
          @click="activeMainTab = 'fortune'"
        >運勢</button>
        <button
          class="main-tab"
          :class="{ active: activeMainTab === 'match' }"
          @click="activeMainTab = 'match'"
        >配對</button>
        <button
          class="main-tab"
          :class="{ active: activeMainTab === 'lucky' }"
          @click="activeMainTab = 'lucky'"
        >吉日</button>
        <button
          class="main-tab"
          :class="{ active: activeMainTab === 'knowledge' }"
          @click="activeMainTab = 'knowledge'"
        >知識</button>
      </nav>

      <!-- Tab 內容區 -->
      <div v-if="mansion" class="tab-content">

        <!-- ==================== 運勢 Tab ==================== -->
        <div v-if="activeMainTab === 'fortune'" class="fortune-tab-content">
          <!-- 運勢子 Tab -->
          <nav class="sub-tabs">
            <button
              class="sub-tab"
              :class="{ active: activeFortuneTab === 'daily' }"
              @click="activeFortuneTab = 'daily'"
            >今日</button>
            <button
              class="sub-tab"
              :class="{ active: activeFortuneTab === 'weekly' }"
              @click="activeFortuneTab = 'weekly'"
            >本週</button>
            <button
              class="sub-tab"
              :class="{ active: activeFortuneTab === 'monthly' }"
              @click="activeFortuneTab = 'monthly'"
            >本月</button>
            <button
              class="sub-tab"
              :class="{ active: activeFortuneTab === 'yearly' }"
              @click="activeFortuneTab = 'yearly'"
            >本年</button>
          </nav>

          <!-- 今日運勢 -->
          <div v-if="activeFortuneTab === 'daily'" class="fortune-panel">
            <div v-if="!dailyFortune" class="loading-state">
              <sl-spinner></sl-spinner>
              <span>載入今日運勢中...</span>
            </div>
            <template v-else>
              <div class="fortune-layout">
                <!-- 左側：分數 + 幸運指南 -->
                <div class="fortune-score-card">
                  <div class="fortune-overall" :class="getFortuneLevel(dailyFortune.fortune.overall).class">
                    <span class="overall-score">{{ dailyFortune.fortune.overall }}</span>
                    <span class="overall-label">{{ getFortuneLevel(dailyFortune.fortune.overall).text }}</span>
                  </div>
                  <div class="fortune-weekday">
                    <ruby>{{ dailyFortune.weekday.name }}<rp>(</rp><rt>{{ dailyFortune.weekday.reading }}</rt><rp>)</rp></ruby>
                    <span class="element-match" :style="{ color: elementColors[dailyFortune.weekday.element] }">
                      {{ dailyFortune.weekday.element }}
                    </span>
                  </div>
                  <!-- 當日宿關係（核心運勢因素） -->
                  <div v-if="dailyFortune.mansion_relation" class="mansion-relation-info">
                    <div class="day-mansion">
                      <span class="relation-label">當日宿</span>
                      <ruby>{{ dailyFortune.day_mansion?.name_jp }}<rp>(</rp><rt>{{ dailyFortune.day_mansion?.reading }}</rt><rp>)</rp></ruby>
                    </div>
                    <div class="relation-type" :class="getMansionRelationClass(dailyFortune.mansion_relation.type)">
                      <span class="relation-name">{{ dailyFortune.mansion_relation.name }}</span>
                      <span class="relation-reading">{{ dailyFortune.mansion_relation.reading }}</span>
                    </div>
                    <p class="relation-desc">{{ dailyFortune.mansion_relation.description }}</p>
                  </div>
                  <div class="lucky-items-compact">
                    <div class="lucky-item">
                      <span class="lucky-label">方位</span>
                      <span class="lucky-value">{{ dailyFortune.lucky.direction }}</span>
                    </div>
                    <div class="lucky-item">
                      <span class="lucky-label">顏色</span>
                      <span class="lucky-value">
                        <span class="color-dot" :style="{ background: dailyFortune.lucky.color_hex }"></span>
                        {{ dailyFortune.lucky.color }}
                      </span>
                    </div>
                    <div class="lucky-item">
                      <span class="lucky-label">數字</span>
                      <span class="lucky-value">{{ dailyFortune.lucky.numbers.join(', ') }}</span>
                    </div>
                  </div>
                </div>

                <!-- 右側：詳細運勢 -->
                <div class="fortune-details-card">
                  <div class="fortune-bars">
                    <div class="fortune-bar-item">
                      <span class="bar-label">事業</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: dailyFortune.fortune.career + '%' }"></div></div>
                      <span class="bar-value">{{ dailyFortune.fortune.career }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">感情</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: dailyFortune.fortune.love + '%' }"></div></div>
                      <span class="bar-value">{{ dailyFortune.fortune.love }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">健康</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: dailyFortune.fortune.health + '%' }"></div></div>
                      <span class="bar-value">{{ dailyFortune.fortune.health }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">財運</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: dailyFortune.fortune.wealth + '%' }"></div></div>
                      <span class="bar-value">{{ dailyFortune.fortune.wealth }}</span>
                    </div>
                  </div>
                  <div class="fortune-advice">
                    <sl-icon name="lightbulb"></sl-icon>
                    <p>{{ dailyFortune.advice }}</p>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <!-- 本週運勢 -->
          <div v-if="activeFortuneTab === 'weekly'" class="fortune-panel">
            <div v-if="!weeklyFortune" class="loading-state">
              <sl-spinner></sl-spinner>
              <span>載入本週運勢中...</span>
            </div>
            <template v-else>
              <div class="fortune-layout">
                <div class="fortune-score-card">
                  <div class="fortune-overall" :class="getFortuneLevel(weeklyFortune.fortune.overall).class">
                    <span class="overall-score">{{ weeklyFortune.fortune.overall }}</span>
                    <span class="overall-label">{{ getFortuneLevel(weeklyFortune.fortune.overall).text }}</span>
                  </div>
                  <div class="fortune-period">
                    <span>第 {{ weeklyFortune.week }} 週</span>
                    <span class="period-range">{{ weeklyFortune.week_start }} ~ {{ weeklyFortune.week_end }}</span>
                  </div>
                  <div class="daily-overview-compact">
                    <div v-for="d in weeklyFortune.daily_overview" :key="d.date" class="day-chip">
                      <span class="day-name">{{ d.weekday }}</span>
                      <span class="day-score" :class="getFortuneLevel(d.score).class">{{ d.score }}</span>
                    </div>
                  </div>
                </div>
                <div class="fortune-details-card">
                  <div class="fortune-bars">
                    <div class="fortune-bar-item">
                      <span class="bar-label">事業</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: weeklyFortune.fortune.career + '%' }"></div></div>
                      <span class="bar-value">{{ weeklyFortune.fortune.career }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">感情</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: weeklyFortune.fortune.love + '%' }"></div></div>
                      <span class="bar-value">{{ weeklyFortune.fortune.love }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">健康</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: weeklyFortune.fortune.health + '%' }"></div></div>
                      <span class="bar-value">{{ weeklyFortune.fortune.health }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">財運</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: weeklyFortune.fortune.wealth + '%' }"></div></div>
                      <span class="bar-value">{{ weeklyFortune.fortune.wealth }}</span>
                    </div>
                  </div>
                  <div class="fortune-advice">
                    <sl-icon name="lightbulb"></sl-icon>
                    <p>{{ weeklyFortune.advice }}</p>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <!-- 本月運勢 -->
          <div v-if="activeFortuneTab === 'monthly'" class="fortune-panel">
            <div v-if="!monthlyFortune" class="loading-state">
              <sl-spinner></sl-spinner>
              <span>載入本月運勢中...</span>
            </div>
            <template v-else>
              <div class="fortune-layout">
                <div class="fortune-score-card">
                  <div class="fortune-overall" :class="getFortuneLevel(monthlyFortune.fortune.overall).class">
                    <span class="overall-score">{{ monthlyFortune.fortune.overall }}</span>
                    <span class="overall-label">{{ getFortuneLevel(monthlyFortune.fortune.overall).text }}</span>
                  </div>
                  <div class="fortune-period">
                    <span>{{ monthlyFortune.year }} 年 {{ monthlyFortune.month }} 月</span>
                  </div>
                  <div class="month-theme">
                    <span class="theme-title">{{ monthlyFortune.theme.title }}</span>
                    <span class="theme-focus">重點：{{ monthlyFortune.theme.focus }}</span>
                  </div>
                  <div class="weekly-overview-compact">
                    <div v-for="w in monthlyFortune.weekly" :key="w.week" class="week-chip">
                      <span class="week-name">W{{ w.week }}</span>
                      <span class="week-score" :class="getFortuneLevel(w.score).class">{{ w.score }}</span>
                    </div>
                  </div>
                </div>
                <div class="fortune-details-card">
                  <div class="fortune-bars">
                    <div class="fortune-bar-item">
                      <span class="bar-label">事業</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: monthlyFortune.fortune.career + '%' }"></div></div>
                      <span class="bar-value">{{ monthlyFortune.fortune.career }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">感情</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: monthlyFortune.fortune.love + '%' }"></div></div>
                      <span class="bar-value">{{ monthlyFortune.fortune.love }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">健康</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: monthlyFortune.fortune.health + '%' }"></div></div>
                      <span class="bar-value">{{ monthlyFortune.fortune.health }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">財運</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: monthlyFortune.fortune.wealth + '%' }"></div></div>
                      <span class="bar-value">{{ monthlyFortune.fortune.wealth }}</span>
                    </div>
                  </div>
                  <div class="fortune-advice">
                    <sl-icon name="lightbulb"></sl-icon>
                    <p>{{ monthlyFortune.advice }}</p>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <!-- 本年運勢 -->
          <div v-if="activeFortuneTab === 'yearly'" class="fortune-panel">
            <div v-if="!yearlyFortune" class="loading-state">
              <sl-spinner></sl-spinner>
              <span>載入本年運勢中...</span>
            </div>
            <template v-else>
              <div class="fortune-layout vertical">
                <div class="fortune-score-card wide">
                  <div class="fortune-overall" :class="getFortuneLevel(yearlyFortune.fortune.overall).class">
                    <span class="overall-score">{{ yearlyFortune.fortune.overall }}</span>
                    <span class="overall-label">{{ getFortuneLevel(yearlyFortune.fortune.overall).text }}</span>
                  </div>
                  <div class="year-info">
                    <ruby class="stem-branch">
                      {{ yearlyFortune.stem.character }}{{ yearlyFortune.branch.character }}
                      <rp>(</rp><rt>{{ yearlyFortune.stem.reading }}{{ yearlyFortune.branch.reading }}</rt><rp>)</rp>
                    </ruby>
                    <span class="zodiac">{{ yearlyFortune.branch.name }}年</span>
                  </div>
                </div>

                <div class="fortune-details-card wide">
                  <div class="fortune-bars">
                    <div class="fortune-bar-item">
                      <span class="bar-label">事業</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: yearlyFortune.fortune.career + '%' }"></div></div>
                      <span class="bar-value">{{ yearlyFortune.fortune.career }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">感情</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: yearlyFortune.fortune.love + '%' }"></div></div>
                      <span class="bar-value">{{ yearlyFortune.fortune.love }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">健康</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: yearlyFortune.fortune.health + '%' }"></div></div>
                      <span class="bar-value">{{ yearlyFortune.fortune.health }}</span>
                    </div>
                    <div class="fortune-bar-item">
                      <span class="bar-label">財運</span>
                      <div class="bar-track"><div class="bar-fill" :style="{ width: yearlyFortune.fortune.wealth + '%' }"></div></div>
                      <span class="bar-value">{{ yearlyFortune.fortune.wealth }}</span>
                    </div>
                  </div>
                </div>

                <!-- 月度趨勢圖 -->
                <div class="monthly-trend-card">
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

                <!-- 機會與注意事項 -->
                <div class="yearly-insights">
                  <div v-if="yearlyFortune.opportunities.length" class="insight-block opportunities">
                    <h4>機會提示</h4>
                    <ul>
                      <li v-for="(opp, idx) in yearlyFortune.opportunities" :key="idx">{{ opp }}</li>
                    </ul>
                  </div>
                  <div v-if="yearlyFortune.warnings.length" class="insight-block warnings">
                    <h4>注意事項</h4>
                    <ul>
                      <li v-for="(warn, idx) in yearlyFortune.warnings" :key="idx">{{ warn }}</li>
                    </ul>
                  </div>
                </div>

                <div class="fortune-advice wide">
                  <sl-icon name="lightbulb"></sl-icon>
                  <p>{{ yearlyFortune.advice }}</p>
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- ==================== 配對 Tab ==================== -->
        <div v-if="activeMainTab === 'match'" class="match-tab-content">
          <!-- 配對子 Tab -->
          <nav class="sub-tabs">
            <button
              class="sub-tab"
              :class="{ active: activeMatchTab === 'finder' }"
              @click="activeMatchTab = 'finder'"
            >尋找配對</button>
            <button
              class="sub-tab"
              :class="{ active: activeMatchTab === 'compat' }"
              @click="activeMatchTab = 'compat'"
            >相性診斷</button>
            <button
              class="sub-tab"
              :class="{ active: activeMatchTab === 'partners' }"
              @click="activeMatchTab = 'partners'"
            >我的配對</button>
          </nav>

          <!-- 尋找配對 -->
          <div v-if="activeMatchTab === 'finder'" class="match-panel">
            <div v-if="finderLoading" class="loading-state">
              <sl-spinner></sl-spinner>
              <span>載入配對資料中...</span>
            </div>
            <template v-else-if="compatFinder">
              <div class="compat-categories">
                <div
                  v-for="relKey in relationKeys"
                  :key="relKey.key"
                  class="compat-category"
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
                  <div class="mansion-chips">
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

          <!-- 相性診斷 -->
          <div v-if="activeMatchTab === 'compat'" class="match-panel">
            <div class="compat-form-section">
              <!-- 未設定自己生日 -->
              <div v-if="!myBirthDate" class="empty-state">
                <sl-icon name="exclamation-circle"></sl-icon>
                <p>請先設定你的生日才能進行相性診斷</p>
                <router-link to="/profile" class="link-btn">前往設定</router-link>
              </div>

              <template v-else>
                <!-- 顯示自己的本命宿 -->
                <div class="my-mansion-display" v-if="mansion">
                  <span class="label">你的本命宿</span>
                  <ruby class="mansion-name">
                    {{ mansion.name_jp }}<rp>(</rp><rt>{{ mansion.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="mansion-element" :style="{ color: elementColors[mansion.element] }">（{{ mansion.element }}）</span>
                </div>

                <div class="compat-input-row">
                  <sl-input
                    type="date"
                    name="compat-person2-birthdate"
                    v-model="date2"
                    label="對方的生日"
                    :max="new Date().toISOString().split('T')[0]"
                  ></sl-input>
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
                </div>
                <div class="compat-vs">
                  <ruby class="relation-name">
                    {{ compatibility.relation.name }}<rp>(</rp><rt>{{ compatibility.relation.reading }}</rt><rp>)</rp>
                  </ruby>
                  <div class="compat-score" :class="getScoreLevel(compatibility.score).class">
                    <span class="score-number">{{ compatibility.score }}</span>
                    <span class="score-label">{{ getScoreLevel(compatibility.score).text }}</span>
                  </div>
                </div>
                <div class="person-card">
                  <ruby class="person-mansion">
                    {{ compatibility.person2.mansion }}<rp>(</rp><rt>{{ compatibility.person2.reading }}</rt><rp>)</rp>
                  </ruby>
                  <span class="person-element" :style="{ color: elementColors[compatibility.person2.element] }">
                    <ruby>{{ compatibility.person2.element }}<rp>(</rp><rt>{{ compatibility.person2.element_reading }}</rt><rp>)</rp></ruby>
                  </span>
                </div>
              </div>

              <div class="compat-summary">
                <p class="description">{{ compatibility.relation.description }}</p>
                <div v-if="compatibility.relation.detailed" class="detailed-section">
                  <p>{{ compatibility.relation.detailed }}</p>
                </div>

                <div class="compat-details-grid">
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
                </div>

                <div v-if="compatibility.relation.good_for?.length" class="good-for-section">
                  <h4>適合的關係</h4>
                  <div class="tag-list">
                    <span v-for="item in compatibility.relation.good_for" :key="item" class="tag">{{ item }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 我的配對 -->
          <div v-if="activeMatchTab === 'partners'" class="match-panel">
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
              <div class="partner-grid">
                <div
                  v-for="pc in partnerCompatibilities"
                  :key="pc.partnerId"
                  class="partner-card"
                >
                  <div class="partner-header">
                    <span class="partner-nickname">{{ pc.nickname }}</span>
                    <span class="partner-score" :class="getScoreColorClass(pc.score)">{{ pc.score }} 分</span>
                  </div>
                  <div class="partner-mansion">
                    <ruby>{{ pc.mansion.name_jp }}<rp>(</rp><rt>{{ pc.mansion.reading }}</rt><rp>)</rp></ruby>
                    <span class="partner-element" :style="{ color: elementColors[pc.mansion.element] }">{{ pc.mansion.element }}</span>
                  </div>
                  <div class="partner-relation">
                    <ruby>{{ pc.relation.name }}<rp>(</rp><rt>{{ pc.relation.reading }}</rt><rp>)</rp></ruby>
                  </div>
                  <div class="partner-bar">
                    <div class="bar-fill" :style="{ width: pc.score + '%' }" :class="getScoreColorClass(pc.score)"></div>
                  </div>
                </div>
              </div>
              <router-link to="/profile" class="add-partner-link">
                <sl-icon name="plus-circle"></sl-icon>
                新增關注對象
              </router-link>
            </template>

            <!-- 尚未載入 -->
            <div v-else class="empty-state">
              <button class="btn-gold" @click="fetchPartnerCompatibilities">
                <sl-icon name="arrow-clockwise"></sl-icon>
                載入配對資料
              </button>
            </div>
          </div>
        </div>

        <!-- ==================== 吉日 Tab ==================== -->
        <div v-if="activeMainTab === 'lucky'" class="lucky-tab-content">
          <!-- 未設定生日提示 -->
          <template v-if="!myBirthDate">
            <div class="empty-state">
              <sl-icon name="calendar-x"></sl-icon>
              <p>請先到「個人資料」設定你的生日</p>
              <router-link to="/profile" class="link-btn">前往設定</router-link>
            </div>
          </template>

          <template v-else>
            <div class="lucky-query-layout">
              <!-- 左側：類別側邊欄 -->
              <aside class="lucky-sidebar">
                <button
                  v-for="cat in luckyDayCategories"
                  :key="cat.key"
                  class="sidebar-category-btn"
                  :class="{ active: selectedLuckyCategory === cat.key }"
                  @click="selectLuckyCategory(cat.key)"
                >
                  <sl-icon :name="cat.icon"></sl-icon>
                  <span>{{ cat.name }}</span>
                </button>
              </aside>

              <!-- 右側：主內容區 -->
              <main class="lucky-main">
                <!-- 未選擇類別 -->
                <div v-if="!selectedLuckyCategory" class="lucky-placeholder">
                  <sl-icon name="arrow-left"></sl-icon>
                  <p>請從左側選擇查詢類型</p>
                </div>

                <!-- 已選擇類別 -->
                <template v-else>
                  <!-- 項目選擇 -->
                  <div class="lucky-action-section">
                    <h4>選擇項目</h4>
                    <div class="action-buttons">
                      <button
                        v-for="action in currentCategoryActions"
                        :key="action.key"
                        class="action-btn"
                        :class="{ active: selectedLuckyAction === action.key }"
                        @click="selectLuckyAction(action.key)"
                      >
                        {{ action.name }}
                      </button>
                    </div>
                  </div>

                  <!-- 載入中 -->
                  <div v-if="luckyDayLoading" class="loading-state">
                    <sl-spinner></sl-spinner>
                    <span>查詢中...</span>
                  </div>

                  <!-- 查詢結果 -->
                  <template v-else-if="luckyDayResult">
                    <!-- 你的本命宿 -->
                    <div class="your-mansion-info">
                      <span class="mansion-badge" :style="{ backgroundColor: elementColors[luckyDayResult.your_mansion.element] }">
                        {{ luckyDayResult.your_mansion.name_jp }}
                      </span>
                      <span class="mansion-reading">{{ luckyDayResult.your_mansion.reading }}</span>
                      <span class="mansion-element">{{ luckyDayResult.your_mansion.element }}性</span>
                      <span class="action-label">{{ luckyDayResult.action_name }}</span>
                    </div>

                    <!-- 吉日/避日雙欄 -->
                    <div class="lucky-result-grid">
                      <!-- 吉日列表 -->
                      <div class="lucky-days-column">
                        <h4>近 30 天吉日</h4>
                        <div v-if="luckyDayResult.lucky_days.length" class="days-list">
                          <div
                            v-for="day in luckyDayResult.lucky_days"
                            :key="day.date"
                            class="day-card lucky"
                            :class="day.rating === '大吉' ? 'excellent' : 'good'"
                          >
                            <div class="day-header">
                              <span class="day-date">{{ formatDate(day.date) }} ({{ day.weekday }})</span>
                              <span class="day-rating">{{ day.rating }}</span>
                            </div>
                            <span class="day-reason">{{ day.reason }}</span>
                          </div>
                        </div>
                        <p v-else class="no-days">暫無吉日</p>
                      </div>

                      <!-- 避日列表 -->
                      <div class="avoid-days-column">
                        <h4>應避開的日期</h4>
                        <div v-if="luckyDayResult.avoid_days.length" class="days-list">
                          <div
                            v-for="day in luckyDayResult.avoid_days"
                            :key="day.date"
                            class="day-card avoid"
                          >
                            <span class="day-date">{{ formatDate(day.date) }} ({{ day.weekday }})</span>
                            <span class="day-reason">{{ day.reason }}</span>
                          </div>
                        </div>
                        <p v-else class="no-days">無需避開</p>
                      </div>
                    </div>

                    <!-- 建議 -->
                    <div v-if="luckyDayResult.advice" class="lucky-advice">
                      <sl-icon name="lightbulb"></sl-icon>
                      <p>{{ luckyDayResult.advice }}</p>
                    </div>
                  </template>
                </template>
              </main>
            </div>
          </template>
        </div>

        <!-- ==================== 知識 Tab ==================== -->
        <div v-if="activeMainTab === 'knowledge'" class="knowledge-tab-content">
          <!-- 本命宿詳情 -->
          <section class="knowledge-section mansion-detail-section">
            <h3>你的本命宿</h3>
            <div class="mansion-detail-card">
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
                <span v-for="kw in mansion.keywords" :key="kw" class="keyword-tag">{{ kw }}</span>
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
          </section>

          <!-- 二十七宿輪盤 -->
          <section v-if="allMansions.length > 0" class="knowledge-section wheel-section">
            <button class="section-toggle" @click="showWheel = !showWheel">
              <h3><ruby>二十七宿<rp>(</rp><rt>にじゅうしちしゅく</rt><rp>)</rp></ruby>輪盤</h3>
              <sl-icon :name="showWheel ? 'chevron-up' : 'chevron-down'"></sl-icon>
            </button>

            <div v-if="showWheel" class="section-content">
              <p class="section-intro">
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
          <section v-if="allRelations.length > 0" class="knowledge-section relations-section">
            <button class="section-toggle" @click="showRelations = !showRelations">
              <h3><ruby>六種關係<rp>(</rp><rt>ろくしゅかんけい</rt><rp>)</rp></ruby>詳解</h3>
              <sl-icon :name="showRelations ? 'chevron-up' : 'chevron-down'"></sl-icon>
            </button>

            <div v-if="showRelations" class="section-content">
              <p class="section-intro">
                宿曜道以「三九秘法」將人際關係分為六種類型。點擊任一關係可展開詳細說明。
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
          <section v-if="allElements.length > 0" class="knowledge-section elements-section">
            <button class="section-toggle" @click="showElements = !showElements">
              <h3><ruby>七曜<rp>(</rp><rt>しちよう</rt><rp>)</rp></ruby>元素詳解</h3>
              <sl-icon :name="showElements ? 'chevron-up' : 'chevron-down'"></sl-icon>
            </button>

            <div v-if="showElements" class="section-content">
              <p class="section-intro">
                七曜（日、月、火、水、木、金、土）對應一週七天，每種元素具有獨特的能量特質。
              </p>

              <div class="element-cards">
                <div
                  v-for="elem in allElements"
                  :key="elem.name"
                  class="element-card"
                  :style="{ borderColor: elementColors[elem.name] }"
                >
                  <div class="element-header">
                    <span class="element-name" :style="{ color: elementColors[elem.name] }">{{ elem.name }}</span>
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
              </div>
            </div>
          </section>

          <!-- 計算公式說明 -->
          <section class="knowledge-section formula-section">
            <button class="section-toggle" @click="showFormula = !showFormula">
              <h3>
                <ruby>月宿傍通曆<rp>(</rp><rt>げっしゅくぼうつうれき</rt><rp>)</rp></ruby>
                計算說明
              </h3>
              <sl-icon :name="showFormula ? 'chevron-up' : 'chevron-down'"></sl-icon>
            </button>

            <div v-if="showFormula" class="section-content">
              <div class="formula-block">
                <h4>本命宿計算公式</h4>
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
              </div>

              <div class="formula-block">
                <h4><ruby>三九秘法<rp>(</rp><rt>さんくひほう</rt><rp>)</rp></ruby>相性計算</h4>
                <p class="formula-desc">根據兩人本命宿的距離判斷六種關係</p>
                <div class="formula-box">
                  <code>距離 = min(|宿A - 宿B|, 27 - |宿A - 宿B|)</code>
                </div>
              </div>
            </div>
          </section>

          <!-- 關於宿曜道 -->
          <section class="knowledge-section history-section">
            <button class="section-toggle" @click="showHistory = !showHistory">
              <h3>關於<ruby>宿曜道<rp>(</rp><rt>しゅくようどう</rt><rp>)</rp></ruby></h3>
              <sl-icon :name="showHistory ? 'chevron-up' : 'chevron-down'"></sl-icon>
            </button>

            <div v-if="showHistory" class="section-content history-content">
              <div class="history-block">
                <h4>起源</h4>
                <p>
                  宿曜道源自古印度的「納沙特拉」占星術，是印度最古老的天文體系之一。
                  此法將黃道周天分為 27 個區域，稱為「二十七宿」。
                </p>
              </div>
              <div class="history-block">
                <h4>傳入日本</h4>
                <p>
                  延曆 23 年（西元 804 年），空海大師入唐求法，歸國時攜回《宿曜經》，
                  成為日本宿曜道的根本經典。
                </p>
              </div>
              <div class="history-block">
                <h4>現代應用</h4>
                <p>
                  時至今日，日本仍廣泛使用宿曜道於婚配、擇日、人事安排等領域。
                  宿曜道的價值在於提供理解人際關係的框架。
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>

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
/* ===== 新版 Tab-based 佈局 ===== */

/* 頂部標題列 */
.page-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) 0;
  margin-bottom: var(--space-4);
}

.page-header-bar h1 {
  margin: 0;
  font-size: 1.75rem;
}

.page-header-bar h1 ruby rt {
  font-size: 0.5em;
  color: var(--text-muted);
}

.query-toggle-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--cosmos-twilight);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.query-toggle-btn:hover,
.query-toggle-btn.active {
  border-color: var(--stellar-gold);
  color: var(--stellar-gold);
}

/* 展開式查詢區 */
.lookup-form-expanded {
  max-width: 600px;
  margin: 0 auto var(--space-6);
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 摘要卡 */
.summary-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  background: linear-gradient(135deg, var(--cosmos-night) 0%, var(--cosmos-twilight) 100%);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}

.summary-left {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
}

.summary-mansion {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--stellar-gold);
}

.summary-mansion rt {
  font-size: 0.4em;
}

.summary-element {
  font-size: 1.1rem;
  font-weight: 500;
}

.summary-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.summary-right.loading {
  justify-content: center;
}

.summary-score {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.summary-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* 未查詢引導 */
.empty-guide {
  text-align: center;
  padding: var(--space-12) var(--space-6);
  margin: var(--space-8) auto;
  max-width: 400px;
}

.empty-guide sl-icon {
  font-size: 3rem;
  color: var(--stellar-gold);
  margin-bottom: var(--space-4);
}

.empty-guide h2 {
  margin-bottom: var(--space-2);
}

.empty-guide p {
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
}

/* 主要 Tab 導航 */
.main-tabs {
  display: flex;
  gap: var(--space-1);
  border-bottom: 1px solid var(--border-default);
  margin-bottom: var(--space-6);
  overflow-x: auto;
}

.main-tab {
  flex: 1;
  padding: var(--space-3) var(--space-6);
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--text-secondary);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.main-tab:hover {
  color: var(--text-primary);
}

.main-tab.active {
  color: var(--stellar-gold);
  border-bottom-color: var(--stellar-gold);
}

/* Tab 內容區 */
.tab-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* 子 Tab */
.fortune-sub-tabs,
.match-sub-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
}

.sub-tab {
  padding: var(--space-2) var(--space-4);
  background: var(--cosmos-twilight);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.sub-tab:hover {
  border-color: var(--stellar-gold);
  color: var(--stellar-gold);
}

.sub-tab.active {
  background: var(--stellar-gold);
  border-color: var(--stellar-gold);
  color: var(--cosmos-night);
}

/* 運勢面板佈局 */
.fortune-panel {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fortune-layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: var(--space-6);
}

.fortune-layout.vertical {
  grid-template-columns: 1fr;
}

.fortune-score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-lg);
  text-align: center;
}

.fortune-score-card .score-number {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
}

.fortune-score-card .score-text {
  font-size: 1rem;
  margin-top: var(--space-2);
}

.fortune-score-card.excellent { color: #4A9B5A; }
.fortune-score-card.good { color: var(--stellar-gold); }
.fortune-score-card.fair { color: #C4A052; }
.fortune-score-card.caution { color: #E89B3C; }
.fortune-score-card.warning { color: #E85D4C; }

/* 當日宿關係資訊 */
.mansion-relation-info {
  margin-top: var(--space-4);
  padding: var(--space-3);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  text-align: center;
}

.mansion-relation-info .day-mansion {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.mansion-relation-info .relation-label {
  opacity: 0.7;
}

.mansion-relation-info .relation-type {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-weight: 600;
}

.mansion-relation-info .relation-reading {
  font-size: 0.75rem;
  opacity: 0.8;
}

.mansion-relation-info .relation-desc {
  margin-top: var(--space-2);
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 關係類型顏色 */
.relation-type.relation-excellent {
  background: rgba(74, 155, 90, 0.3);
  color: #4A9B5A;
}
.relation-type.relation-good {
  background: rgba(196, 160, 82, 0.3);
  color: var(--stellar-gold);
}
.relation-type.relation-fair {
  background: rgba(160, 140, 100, 0.3);
  color: #B0A070;
}
.relation-type.relation-neutral {
  background: rgba(100, 100, 100, 0.3);
  color: var(--text-secondary);
}
.relation-type.relation-caution {
  background: rgba(232, 155, 60, 0.3);
  color: #E89B3C;
}
.relation-type.relation-warning {
  background: rgba(232, 93, 76, 0.3);
  color: #E85D4C;
}

.fortune-score-card.large {
  padding: var(--space-4);
}

.lucky-info,
.theme-info {
  margin-top: var(--space-4);
  font-size: 0.85rem;
}

.lucky-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
  color: var(--text-secondary);
}

.fortune-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.fortune-date-info {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-3);
}

.fortune-date-info .weekday {
  font-size: 1.1rem;
  font-weight: 500;
}

.fortune-date-info .date-range,
.fortune-date-info .month-label {
  font-size: 1.1rem;
  font-weight: 500;
}

.fortune-bars {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.fortune-bar-item {
  display: grid;
  grid-template-columns: 50px 1fr 40px;
  align-items: center;
  gap: var(--space-3);
}

.bar-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.bar-track {
  height: 8px;
  background: var(--cosmos-night);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: var(--stellar-gold);
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.bar-value {
  font-size: 0.9rem;
  text-align: right;
  color: var(--text-secondary);
}

.fortune-advice {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  line-height: 1.6;
}

.daily-overview-grid {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.daily-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  min-width: 50px;
}

.daily-item .day-name {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.daily-item .day-score {
  font-size: 1rem;
  font-weight: 600;
}

.weekly-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-3);
}

.weekly-item {
  display: flex;
  flex-direction: column;
  padding: var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.week-num {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.week-score {
  font-size: 1.25rem;
  font-weight: 600;
}

.week-focus {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: var(--space-1);
}

/* 月度趨勢圖 */
.monthly-trend h4 {
  margin-bottom: var(--space-3);
}

.trend-chart {
  display: flex;
  align-items: flex-end;
  height: 120px;
  gap: 4px;
  padding: var(--space-2) 0;
}

.trend-bar {
  flex: 1;
  min-height: 10px;
  background: var(--stellar-gold);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  position: relative;
}

.trend-bar .trend-value {
  font-size: 0.65rem;
  color: var(--text-muted);
  position: absolute;
  top: -18px;
}

.trend-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--text-muted);
}

/* 配對面板 */
.match-panel {
  animation: fadeIn 0.2s ease-out;
}

.my-mansion-info,
.my-mansion-display {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
  padding: var(--space-3);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.my-mansion-info .label,
.my-mansion-display .label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.compat-categories {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.compat-category {
  padding: var(--space-4);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--stellar-gold);
}

.compat-category.avoid {
  border-left-color: #E85D4C;
}

.compat-category .category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.compat-category .category-name {
  font-size: 1.1rem;
  font-weight: 500;
}

.compat-category .category-desc {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: var(--space-3);
}

.mansion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.mansion-chip {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-night);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.mansion-chip:hover {
  border-color: var(--stellar-gold);
}

.mansion-chip.active {
  border-color: var(--stellar-gold);
  background: rgba(212, 175, 55, 0.1);
}

.mansion-chip.danger:hover,
.mansion-chip.danger.active {
  border-color: #E85D4C;
  background: rgba(232, 93, 76, 0.1);
}

.chip-element {
  font-size: 0.85rem;
}

.selected-mansion-detail {
  margin-top: var(--space-6);
  padding: var(--space-4);
}

/* 相性結果 */
.compat-form {
  margin-bottom: var(--space-6);
}

.compat-result {
  margin-top: var(--space-6);
}

.compat-pair {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.person-card {
  text-align: center;
  padding: var(--space-4);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
  min-width: 120px;
}

.person-mansion {
  font-size: 1.25rem;
  font-weight: 500;
  display: block;
  margin-bottom: var(--space-2);
}

.compat-vs {
  padding: var(--space-2) var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-full);
}

.compat-score {
  text-align: center;
  margin-bottom: var(--space-4);
}

.compat-score .score-number {
  font-size: 3rem;
  font-weight: 700;
}

.compat-score .score-label {
  display: block;
  font-size: 1rem;
}

.compat-summary {
  padding: var(--space-4);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

/* 我的配對 */
.partner-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.partner-compat-card {
  padding: var(--space-4);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-md);
}

.pc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.pc-nickname {
  font-size: 1.1rem;
  font-weight: 500;
}

.pc-score {
  font-weight: 600;
}

.pc-mansion {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.pc-arrow {
  color: var(--text-muted);
}

.pc-relation {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.pc-relation-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.pc-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-3);
}

.pc-score-bar {
  height: 6px;
  background: var(--cosmos-night);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.add-partner-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3);
  color: var(--stellar-gold);
  text-decoration: none;
  margin-top: var(--space-4);
}

/* 吉日 Tab */
.lucky-tab {
  animation: fadeIn 0.2s ease-out;
}

/* 知識 Tab */
.knowledge-tab {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* 運勢分數顏色 */
.excellent { color: #4A9B5A; }
.good { color: var(--stellar-gold); }
.fair { color: #C4A052; }
.caution { color: #E89B3C; }
.warning { color: #E85D4C; }

/* 響應式 */
@media (max-width: 768px) {
  .page-header-bar {
    flex-wrap: wrap;
    gap: var(--space-3);
  }

  .summary-card {
    flex-direction: column;
    text-align: center;
    gap: var(--space-3);
  }

  .summary-left {
    justify-content: center;
  }

  .summary-right {
    align-items: center;
  }

  .main-tabs {
    gap: 0;
  }

  .main-tab {
    flex: none;
    padding: var(--space-3) var(--space-4);
    font-size: 0.9rem;
  }

  .fortune-layout {
    grid-template-columns: 1fr;
  }

  .fortune-score-card {
    width: 100%;
  }

  .fortune-bar-item {
    grid-template-columns: 40px 1fr 35px;
  }

  .compat-pair {
    flex-direction: column;
  }

  .person-card {
    width: 100%;
  }

  .compat-vs {
    margin: var(--space-2) 0;
  }
}

/* ===== 原有樣式 ===== */

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

/* 吉日查詢 */
.lucky-query-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.lucky-query-content .no-data {
  color: var(--text-muted);
  text-align: center;
  padding: var(--space-6);
}

/* 側邊欄 + 主內容區 Layout */
.lucky-query-layout {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: var(--space-4);
  min-height: 400px;
}

/* 左側側邊欄 */
.lucky-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  padding: var(--space-2);
}

.sidebar-category-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  font-size: 0.9rem;
}

.sidebar-category-btn:hover {
  background: var(--cosmos-twilight);
  color: var(--text-primary);
}

.sidebar-category-btn.active {
  background: var(--stellar-gold);
  color: var(--cosmos-night);
}

.sidebar-category-btn sl-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

/* 右側主內容區 */
.lucky-main {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.lucky-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  height: 100%;
  color: var(--text-muted);
}

.lucky-placeholder sl-icon {
  font-size: 2rem;
}

.lucky-main .loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-6);
  color: var(--text-muted);
}

/* 項目選擇 */
.lucky-action-section h4 {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 400;
  margin-bottom: var(--space-2);
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.action-btn {
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-night);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-pill);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
}

.action-btn:hover {
  background: var(--cosmos-twilight);
  border-color: var(--text-muted);
}

.action-btn.active {
  background: var(--nebula-purple);
  border-color: var(--nebula-purple);
  color: var(--text-primary);
}

/* 本命宿資訊 */
.your-mansion-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.your-mansion-info .mansion-badge {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  color: white;
  font-weight: 500;
  font-size: 0.85rem;
}

.your-mansion-info .mansion-reading {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.your-mansion-info .mansion-element {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.your-mansion-info .action-label {
  margin-left: auto;
  padding: var(--space-1) var(--space-2);
  background: var(--nebula-purple);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.8rem;
}

/* 吉日/避日雙欄 */
.lucky-result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.lucky-days-column h4,
.avoid-days-column h4 {
  color: var(--stellar-gold);
  font-size: 0.9rem;
  margin-bottom: var(--space-3);
}

.avoid-days-column h4 {
  color: #E85D4C;
}

.days-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.day-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.day-card.lucky.excellent {
  border-left: 3px solid #4A9B5A;
}

.day-card.lucky.good {
  border-left: 3px solid var(--stellar-gold);
}

.day-card.avoid {
  border-left: 3px solid #E85D4C;
}

.day-card .day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.day-card .day-date {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.85rem;
}

.day-card .day-rating {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(74, 155, 90, 0.2);
  color: #4A9B5A;
}

.day-card.good .day-rating {
  background: rgba(196, 160, 82, 0.2);
  color: var(--stellar-gold);
}

.day-card .day-reason {
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.4;
}

.no-days {
  color: var(--text-muted);
  font-size: 0.85rem;
  text-align: center;
  padding: var(--space-4);
}

/* 建議區塊 */
.lucky-advice {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--stellar-gold);
}

.lucky-advice sl-icon {
  color: var(--stellar-gold);
  font-size: 1.2rem;
  flex-shrink: 0;
}

.lucky-advice p {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 0.85rem;
  margin: 0;
}

/* RWD: Mobile */
@media (max-width: 768px) {
  .lucky-query-layout {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .lucky-sidebar {
    flex-direction: row;
    overflow-x: auto;
    padding: var(--space-2);
    gap: var(--space-2);
    -webkit-overflow-scrolling: touch;
  }

  .sidebar-category-btn {
    flex-direction: column;
    padding: var(--space-2);
    min-width: 60px;
    text-align: center;
    font-size: 0.75rem;
    gap: var(--space-1);
  }

  .sidebar-category-btn sl-icon {
    font-size: 1.2rem;
  }

  .lucky-placeholder {
    padding: var(--space-6);
  }

  .lucky-placeholder sl-icon {
    transform: rotate(-90deg);
  }

  .lucky-placeholder p {
    text-align: center;
  }

  .lucky-result-grid {
    grid-template-columns: 1fr;
  }

  .avoid-days-column {
    border-top: 1px solid var(--border-default);
    padding-top: var(--space-4);
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
