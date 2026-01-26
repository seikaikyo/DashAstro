<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useProfile } from '../stores/profile'
import MansionWheel from '../components/MansionWheel.vue'

const { profile, myBirthDate, partnersWithBirthDate } = useProfile()

// ============================================================================
// Type Definitions
// ============================================================================

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

interface FortuneScores {
  overall: number
  career: number
  love: number
  health: number
  wealth: number
}

interface MansionRelation {
  type: string
  name: string
  reading: string
  description: string
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
  day_mansion: {
    name_jp: string
    reading: string
    element: string
    index: number
  }
  mansion_relation: MansionRelation
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

interface LunarDate {
  lunar_month: number
  lunar_month_name: string
  lunar_day: number
  display: string
  solar_dates?: { lunar_year: number; solar_date: string; display: string }[]
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
  mei: CompatibilityCategory
  gyotai: CompatibilityCategory
  eishin: CompatibilityCategory
  yusui: CompatibilityCategory
  ankai: CompatibilityCategory
  kisei: CompatibilityCategory
}

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

interface WheelMansion {
  index: number
  name_jp: string
  name_zh: string
  reading: string
  element: string
  personality?: string
  keywords?: string[]
}

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

interface ElementType {
  name: string
  reading: string
  planet: string
  traits: string
  energy: string
}

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

// ============================================================================
// State
// ============================================================================

const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'

// Tab Navigation
const activeMainTab = ref<'fortune' | 'match' | 'lucky' | 'knowledge'>('fortune')
const activeFortuneTab = ref<'daily' | 'weekly' | 'monthly' | 'yearly'>('daily')
const activeMatchTab = ref<'finder' | 'compat' | 'partners'>('finder')
const activeKnowledgeTab = ref<'mansion' | 'wheel' | 'relations' | 'elements' | 'calendar' | 'history'>('mansion')

// Query UI
const showQueryDialog = ref(false)
const birthDate = ref('')
const lookupLoading = ref(false)
const lookupError = ref('')

// Mansion Data
const mansion = ref<Mansion | null>(null)
const metadata = ref<Metadata | null>(null)
const allMansions = ref<WheelMansion[]>([])
const allRelations = ref<RelationType[]>([])
const allElements = ref<ElementType[]>([])
const selectedWheelMansion = ref<WheelMansion | null>(null)

// Fortune Data
const dailyFortune = ref<DailyFortune | null>(null)
const weeklyFortune = ref<WeeklyFortune | null>(null)
const monthlyFortune = ref<MonthlyFortune | null>(null)
const yearlyFortune = ref<YearlyFortune | null>(null)
const fortuneLoading = ref(false)

// Compatibility
const compatFinder = ref<CompatibilityFinderResult | null>(null)
const finderLoading = ref(false)
const selectedMansion = ref<CompatibleMansion | null>(null)
const expandedLunarDates = ref<number[]>([])

// Pair Diagnosis
const date2 = ref('')
const compatibility = ref<CompatibilityResult | null>(null)
const compatLoading = ref(false)
const compatError = ref('')

// Partner Compatibilities
const partnerCompatibilities = ref<PartnerCompatibility[]>([])
const partnerCompatLoading = ref(false)

// Lucky Days
const luckyDayCategories = ref<LuckyDayCategory[]>([])
const selectedLuckyCategory = ref<string | null>(null)
const selectedLuckyAction = ref<string | null>(null)
const luckyDayResult = ref<LuckyDayResult | null>(null)
const luckyDayLoading = ref(false)

// Knowledge
const expandedRelation = ref<string | null>(null)

// ============================================================================
// Computed
// ============================================================================

const elementColors: Record<string, string> = {
  '': '#a8a29e',
  '': '#C4A052',
  '': '#8B7355',
  '': '#E89B3C',
  '': '#7CB3D9',
  '': '#E85D4C',
  '': '#5B8FA8'
}

const mansionElementColor = computed(() => {
  return mansion.value ? elementColors[mansion.value.element] || '#f59e0b' : '#f59e0b'
})

const currentCategoryActions = computed(() => {
  if (!selectedLuckyCategory.value) return []
  const cat = luckyDayCategories.value.find(c => c.key === selectedLuckyCategory.value)
  return cat?.actions || []
})

const relationKeys = [
  { key: 'eishin', cssClass: 'excellent' },
  { key: 'gyotai', cssClass: 'good' },
  { key: 'mei', cssClass: 'fair' },
  { key: 'kisei', cssClass: 'caution' },
  { key: 'yusui', cssClass: 'neutral' },
  { key: 'ankai', cssClass: 'warning' }
]

// ============================================================================
// Helper Functions
// ============================================================================

function getFortuneLevel(score: number) {
  if (score >= 90) return { text: '大吉', class: 'excellent' }
  if (score >= 75) return { text: '', class: 'good' }
  if (score >= 60) return { text: '中吉', class: 'fair' }
  if (score >= 45) return { text: '小吉', class: 'caution' }
  return { text: '', class: 'warning' }
}

function getMansionRelationClass(relationType: string) {
  const classMap: Record<string, string> = {
    'eishin': 'excellent',
    'gyotai': 'good',
    'mei': 'fair',
    'yusui': 'neutral',
    'kisei': 'caution',
    'ankai': 'warning'
  }
  return classMap[relationType] || 'neutral'
}

function getScoreClass(score: number) {
  if (score >= 90) return 'excellent'
  if (score >= 75) return 'good'
  if (score >= 60) return 'fair'
  if (score >= 45) return 'caution'
  return 'warning'
}

function getScoreLevel(score: number) {
  if (score >= 90) return { text: '天作之合', class: 'excellent' }
  if (score >= 75) return { text: '相當不錯', class: 'good' }
  if (score >= 60) return { text: '需要磨合', class: 'fair' }
  return { text: '多加小心', class: 'warning' }
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

// ============================================================================
// API Functions
// ============================================================================

async function lookupMansion() {
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
        showQueryDialog.value = false
        fetchCompatibleMansions()
        fetchAllFortunes()
      } else {
        lookupError.value = data.error || '查詢失敗'
      }
    } else {
      const err = await res.json()
      lookupError.value = err.detail || '查詢失敗'
    }
  } catch {
    lookupError.value = '無法連線到伺服器'
  } finally {
    lookupLoading.value = false
  }
}

async function fetchCompatibleMansions() {
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
  } catch {
    console.error('Failed to fetch compatible mansions')
  } finally {
    finderLoading.value = false
  }
}

async function fetchDailyFortune() {
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
  } catch {
    console.error('Failed to fetch daily fortune')
  } finally {
    fortuneLoading.value = false
  }
}

async function fetchWeeklyFortune() {
  if (!birthDate.value) return
  fortuneLoading.value = true

  const now = new Date()
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
  } catch {
    console.error('Failed to fetch weekly fortune')
  } finally {
    fortuneLoading.value = false
  }
}

async function fetchMonthlyFortune() {
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
  } catch {
    console.error('Failed to fetch monthly fortune')
  } finally {
    fortuneLoading.value = false
  }
}

async function fetchYearlyFortune() {
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
  } catch {
    console.error('Failed to fetch yearly fortune')
  } finally {
    fortuneLoading.value = false
  }
}

async function fetchAllFortunes() {
  await Promise.all([
    fetchDailyFortune(),
    fetchWeeklyFortune(),
    fetchMonthlyFortune(),
    fetchYearlyFortune()
  ])
}

async function fetchLuckyDayCategories() {
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/lucky-days/categories`)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        luckyDayCategories.value = data.categories
      }
    }
  } catch {
    console.error('Failed to fetch lucky day categories')
  }
}

async function fetchLuckyDays() {
  const queryDate = birthDate.value || myBirthDate.value
  if (!queryDate || !selectedLuckyCategory.value || !selectedLuckyAction.value) return

  luckyDayLoading.value = true
  luckyDayResult.value = null

  try {
    const res = await fetch(
      `${apiUrl}/api/sukuyodo/lucky-days/${queryDate}?category=${selectedLuckyCategory.value}&action=${selectedLuckyAction.value}`
    )
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        luckyDayResult.value = data.data
      }
    }
  } catch {
    console.error('Failed to fetch lucky days')
  } finally {
    luckyDayLoading.value = false
  }
}

async function calculateCompatibility() {
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
  } catch {
    compatError.value = '無法連線到伺服器'
  } finally {
    compatLoading.value = false
  }
}

async function fetchPartnerCompatibilities() {
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

    partnerCompatibilities.value = results.sort((a, b) => b.score - a.score)
  } catch {
    console.error('Failed to fetch partner compatibilities')
  } finally {
    partnerCompatLoading.value = false
  }
}

// ============================================================================
// Event Handlers
// ============================================================================

function selectLuckyCategory(categoryKey: string) {
  selectedLuckyCategory.value = categoryKey
  selectedLuckyAction.value = null
  luckyDayResult.value = null
}

function selectLuckyAction(actionKey: string) {
  selectedLuckyAction.value = actionKey
  fetchLuckyDays()
}

function handleWheelSelect(m: WheelMansion) {
  if (selectedWheelMansion.value?.index === m.index) {
    selectedWheelMansion.value = null
  } else {
    selectedWheelMansion.value = m
  }
}

function toggleRelation(type: string) {
  expandedRelation.value = expandedRelation.value === type ? null : type
}

function toggleLunarDate(ld: LunarDate) {
  const idx = expandedLunarDates.value.indexOf(ld.lunar_month)
  if (idx >= 0) {
    expandedLunarDates.value.splice(idx, 1)
  } else {
    expandedLunarDates.value.push(ld.lunar_month)
  }
}

function quickSelect(date: string) {
  birthDate.value = date
  lookupMansion()
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  // Load metadata
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/metadata`)
    if (res.ok) {
      metadata.value = await res.json()
    }
  } catch {
    console.error('Failed to load metadata')
  }

  // Load all mansions
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/mansions`)
    if (res.ok) {
      const data = await res.json()
      if (data.success && data.mansions) {
        allMansions.value = data.mansions
      }
    }
  } catch {
    console.error('Failed to load mansions')
  }

  // Load relations
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/relations`)
    if (res.ok) {
      const data = await res.json()
      if (data.relations) {
        allRelations.value = data.relations
      }
    }
  } catch {
    console.error('Failed to load relations')
  }

  // Load elements
  try {
    const res = await fetch(`${apiUrl}/api/sukuyodo/elements`)
    if (res.ok) {
      const data = await res.json()
      if (data.elements) {
        allElements.value = data.elements
      }
    }
  } catch {
    console.error('Failed to load elements')
  }

  // Load lucky day categories
  fetchLuckyDayCategories()

  // Auto-load if profile has birthdate
  if (myBirthDate.value) {
    birthDate.value = myBirthDate.value
    lookupMansion()
  }
})

// Watch for partner tab switch
watch(activeMatchTab, (tab) => {
  if (tab === 'partners' && partnerCompatibilities.value.length === 0) {
    fetchPartnerCompatibilities()
  }
})
</script>

<template>
  <div class="sukuyodo-v2">
    <!-- Header -->
    <header class="header">
      <h1 class="header-title">
        <ruby>宿曜道<rp>(</rp><rt>しゅくようどう</rt><rp>)</rp></ruby>
      </h1>
      <button class="btn-query" @click="showQueryDialog = true">
        <sl-icon name="search"></sl-icon>
        <span>查詢本命宿</span>
      </button>
    </header>

    <!-- Query Dialog -->
    <sl-dialog
      :open="showQueryDialog"
      label="查詢本命宿"
      class="query-dialog"
      @sl-hide="showQueryDialog = false"
    >
      <div class="query-content">
        <p class="query-desc">輸入西曆生日，系統會自動轉換為農曆並計算你的本命宿</p>

        <!-- Quick Select -->
        <div v-if="myBirthDate || partnersWithBirthDate.length > 0" class="quick-select">
          <span class="quick-label">快速選擇：</span>
          <div class="quick-btns">
            <button
              v-if="myBirthDate"
              class="quick-btn"
              :class="{ active: birthDate === myBirthDate }"
              @click="quickSelect(myBirthDate)"
            >我</button>
            <button
              v-for="p in partnersWithBirthDate"
              :key="p.id"
              class="quick-btn"
              :class="{ active: birthDate === p.birthDate }"
              @click="quickSelect(p.birthDate!)"
            >{{ p.nickname }}</button>
          </div>
        </div>

        <div class="query-form">
          <sl-input
            type="date"
            v-model="birthDate"
            label="西曆生日"
            :max="new Date().toISOString().split('T')[0]"
          ></sl-input>
        </div>

        <div v-if="lookupError" class="error-msg">{{ lookupError }}</div>
      </div>

      <div slot="footer" class="dialog-footer">
        <sl-button variant="default" @click="showQueryDialog = false">取消</sl-button>
        <sl-button
          variant="primary"
          :loading="lookupLoading"
          :disabled="!birthDate"
          @click="lookupMansion"
        >查詢</sl-button>
      </div>
    </sl-dialog>

    <!-- Summary Card -->
    <section v-if="mansion" class="summary-card">
      <div class="summary-main">
        <div class="summary-mansion">
          <span class="mansion-star">&#9733;</span>
          <ruby class="mansion-name">
            {{ mansion.name_jp }}<rp>(</rp><rt>{{ mansion.reading }}</rt><rp>)</rp>
          </ruby>
          <span class="mansion-element" :style="{ background: mansionElementColor }">
            {{ mansion.element }}
          </span>
        </div>
        <p class="mansion-desc">{{ mansion.personality }}</p>
        <div v-if="dailyFortune?.mansion_relation" class="mansion-relation" :class="getMansionRelationClass(dailyFortune.mansion_relation.type)">
          今日與本命宿關係：{{ dailyFortune.mansion_relation.name }}（{{ dailyFortune.mansion_relation.reading }}）- {{ dailyFortune.mansion_relation.description }}
        </div>
      </div>
      <div class="summary-fortune">
        <template v-if="dailyFortune">
          <div class="fortune-score" :class="getFortuneLevel(dailyFortune.fortune.overall).class">
            {{ dailyFortune.fortune.overall }}
          </div>
          <div class="fortune-label">今日運勢</div>
          <div class="fortune-level" :class="getFortuneLevel(dailyFortune.fortune.overall).class">
            {{ getFortuneLevel(dailyFortune.fortune.overall).text }}
          </div>
        </template>
        <sl-spinner v-else></sl-spinner>
      </div>
    </section>

    <!-- Empty State -->
    <section v-if="!mansion" class="empty-state">
      <sl-icon name="stars"></sl-icon>
      <h2>探索你的本命宿</h2>
      <p>了解你的命宿特質與每日運勢</p>
      <button class="btn-primary" @click="showQueryDialog = true">開始查詢</button>
    </section>

    <!-- Main Tabs -->
    <nav v-if="mansion" class="main-tabs">
      <button
        class="tab-btn"
        :class="{ active: activeMainTab === 'fortune' }"
        @click="activeMainTab = 'fortune'"
      >運勢</button>
      <button
        class="tab-btn"
        :class="{ active: activeMainTab === 'match' }"
        @click="activeMainTab = 'match'"
      >配對</button>
      <button
        class="tab-btn"
        :class="{ active: activeMainTab === 'lucky' }"
        @click="activeMainTab = 'lucky'"
      >吉日</button>
      <button
        class="tab-btn"
        :class="{ active: activeMainTab === 'knowledge' }"
        @click="activeMainTab = 'knowledge'"
      >知識</button>
    </nav>

    <!-- Tab Content -->
    <main v-if="mansion" class="tab-content">
      <!-- Fortune Tab -->
      <section v-if="activeMainTab === 'fortune'" class="fortune-tab">
        <div class="sub-tabs">
          <button
            class="pill-btn"
            :class="{ active: activeFortuneTab === 'daily' }"
            @click="activeFortuneTab = 'daily'"
          >今日</button>
          <button
            class="pill-btn"
            :class="{ active: activeFortuneTab === 'weekly' }"
            @click="activeFortuneTab = 'weekly'"
          >本週</button>
          <button
            class="pill-btn"
            :class="{ active: activeFortuneTab === 'monthly' }"
            @click="activeFortuneTab = 'monthly'"
          >本月</button>
          <button
            class="pill-btn"
            :class="{ active: activeFortuneTab === 'yearly' }"
            @click="activeFortuneTab = 'yearly'"
          >本年</button>
        </div>

        <!-- Daily Fortune -->
        <div v-if="activeFortuneTab === 'daily'" class="fortune-content">
          <template v-if="dailyFortune">
            <div class="fortune-card">
              <h3 class="fortune-title">
                {{ dailyFortune.date }} {{ dailyFortune.weekday.name }}
                <span class="weekday-element">({{ dailyFortune.weekday.element }}曜)</span>
              </h3>

              <div class="score-bars">
                <div class="score-row">
                  <span class="score-label">事業</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(dailyFortune.fortune.career)" :style="{ width: dailyFortune.fortune.career + '%' }"></div>
                  </div>
                  <span class="score-value">{{ dailyFortune.fortune.career }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">感情</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(dailyFortune.fortune.love)" :style="{ width: dailyFortune.fortune.love + '%' }"></div>
                  </div>
                  <span class="score-value">{{ dailyFortune.fortune.love }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">健康</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(dailyFortune.fortune.health)" :style="{ width: dailyFortune.fortune.health + '%' }"></div>
                  </div>
                  <span class="score-value">{{ dailyFortune.fortune.health }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">財運</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(dailyFortune.fortune.wealth)" :style="{ width: dailyFortune.fortune.wealth + '%' }"></div>
                  </div>
                  <span class="score-value">{{ dailyFortune.fortune.wealth }}</span>
                </div>
              </div>

              <div class="lucky-info">
                <div class="lucky-item">
                  <span class="lucky-label">幸運色</span>
                  <span class="lucky-value">
                    <span class="color-dot" :style="{ background: dailyFortune.lucky.color_hex }"></span>
                    {{ dailyFortune.lucky.color }}
                  </span>
                </div>
                <div class="lucky-item">
                  <span class="lucky-label">幸運方位</span>
                  <span class="lucky-value">{{ dailyFortune.lucky.direction }}</span>
                </div>
                <div class="lucky-item">
                  <span class="lucky-label">幸運數字</span>
                  <span class="lucky-value">{{ dailyFortune.lucky.numbers.join(', ') }}</span>
                </div>
              </div>

              <div class="advice-box">
                <h4>今日建議</h4>
                <p>{{ dailyFortune.advice }}</p>
              </div>
            </div>
          </template>
          <div v-else class="loading-state">
            <sl-spinner></sl-spinner>
          </div>
        </div>

        <!-- Weekly Fortune -->
        <div v-if="activeFortuneTab === 'weekly'" class="fortune-content">
          <template v-if="weeklyFortune">
            <div class="fortune-card">
              <h3 class="fortune-title">
                第 {{ weeklyFortune.week }} 週
                <span class="date-range">({{ weeklyFortune.week_start }} ~ {{ weeklyFortune.week_end }})</span>
              </h3>

              <div class="score-bars">
                <div class="score-row">
                  <span class="score-label">整體</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(weeklyFortune.fortune.overall)" :style="{ width: weeklyFortune.fortune.overall + '%' }"></div>
                  </div>
                  <span class="score-value">{{ weeklyFortune.fortune.overall }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">事業</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(weeklyFortune.fortune.career)" :style="{ width: weeklyFortune.fortune.career + '%' }"></div>
                  </div>
                  <span class="score-value">{{ weeklyFortune.fortune.career }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">感情</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(weeklyFortune.fortune.love)" :style="{ width: weeklyFortune.fortune.love + '%' }"></div>
                  </div>
                  <span class="score-value">{{ weeklyFortune.fortune.love }}</span>
                </div>
              </div>

              <div class="daily-overview">
                <h4>每日概覽</h4>
                <div class="daily-list">
                  <div
                    v-for="day in weeklyFortune.daily_overview"
                    :key="day.date"
                    class="daily-item"
                    :class="getScoreClass(day.score)"
                  >
                    <span class="day-date">{{ formatDate(day.date) }}</span>
                    <span class="day-weekday">{{ day.weekday }}</span>
                    <span class="day-score">{{ day.score }}</span>
                  </div>
                </div>
              </div>

              <div class="advice-box">
                <h4>本週建議</h4>
                <p>{{ weeklyFortune.advice }}</p>
              </div>
            </div>
          </template>
          <div v-else class="loading-state">
            <sl-spinner></sl-spinner>
          </div>
        </div>

        <!-- Monthly Fortune -->
        <div v-if="activeFortuneTab === 'monthly'" class="fortune-content">
          <template v-if="monthlyFortune">
            <div class="fortune-card">
              <h3 class="fortune-title">
                {{ monthlyFortune.year }} 年 {{ monthlyFortune.month }} 月
              </h3>

              <div v-if="monthlyFortune.theme" class="theme-box">
                <h4>{{ monthlyFortune.theme.title }}</h4>
                <p>{{ monthlyFortune.theme.focus }}</p>
              </div>

              <div class="score-bars">
                <div class="score-row">
                  <span class="score-label">整體</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(monthlyFortune.fortune.overall)" :style="{ width: monthlyFortune.fortune.overall + '%' }"></div>
                  </div>
                  <span class="score-value">{{ monthlyFortune.fortune.overall }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">事業</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(monthlyFortune.fortune.career)" :style="{ width: monthlyFortune.fortune.career + '%' }"></div>
                  </div>
                  <span class="score-value">{{ monthlyFortune.fortune.career }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">感情</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(monthlyFortune.fortune.love)" :style="{ width: monthlyFortune.fortune.love + '%' }"></div>
                  </div>
                  <span class="score-value">{{ monthlyFortune.fortune.love }}</span>
                </div>
              </div>

              <div class="weekly-overview">
                <h4>每週概覽</h4>
                <div class="weekly-list">
                  <div
                    v-for="w in monthlyFortune.weekly"
                    :key="w.week"
                    class="weekly-item"
                  >
                    <span class="week-num">第 {{ w.week }} 週</span>
                    <div class="week-bar">
                      <div class="week-fill" :class="getScoreClass(w.score)" :style="{ width: w.score + '%' }"></div>
                    </div>
                    <span class="week-score">{{ w.score }}</span>
                  </div>
                </div>
              </div>

              <div class="advice-box">
                <h4>本月建議</h4>
                <p>{{ monthlyFortune.advice }}</p>
              </div>
            </div>
          </template>
          <div v-else class="loading-state">
            <sl-spinner></sl-spinner>
          </div>
        </div>

        <!-- Yearly Fortune -->
        <div v-if="activeFortuneTab === 'yearly'" class="fortune-content">
          <template v-if="yearlyFortune">
            <div class="fortune-card">
              <h3 class="fortune-title">
                {{ yearlyFortune.year }} 年運勢
                <span class="year-info">({{ yearlyFortune.stem.character }}{{ yearlyFortune.branch.character }}年)</span>
              </h3>

              <div class="score-bars">
                <div class="score-row">
                  <span class="score-label">整體</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(yearlyFortune.fortune.overall)" :style="{ width: yearlyFortune.fortune.overall + '%' }"></div>
                  </div>
                  <span class="score-value">{{ yearlyFortune.fortune.overall }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">事業</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(yearlyFortune.fortune.career)" :style="{ width: yearlyFortune.fortune.career + '%' }"></div>
                  </div>
                  <span class="score-value">{{ yearlyFortune.fortune.career }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">感情</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(yearlyFortune.fortune.love)" :style="{ width: yearlyFortune.fortune.love + '%' }"></div>
                  </div>
                  <span class="score-value">{{ yearlyFortune.fortune.love }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">健康</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(yearlyFortune.fortune.health)" :style="{ width: yearlyFortune.fortune.health + '%' }"></div>
                  </div>
                  <span class="score-value">{{ yearlyFortune.fortune.health }}</span>
                </div>
                <div class="score-row">
                  <span class="score-label">財運</span>
                  <div class="score-bar">
                    <div class="score-fill" :class="getScoreClass(yearlyFortune.fortune.wealth)" :style="{ width: yearlyFortune.fortune.wealth + '%' }"></div>
                  </div>
                  <span class="score-value">{{ yearlyFortune.fortune.wealth }}</span>
                </div>
              </div>

              <div v-if="yearlyFortune.opportunities?.length" class="opportunities">
                <h4>機會提示</h4>
                <ul>
                  <li v-for="(opp, i) in yearlyFortune.opportunities" :key="i">{{ opp }}</li>
                </ul>
              </div>

              <div v-if="yearlyFortune.warnings?.length" class="warnings">
                <h4>注意事項</h4>
                <ul>
                  <li v-for="(warn, i) in yearlyFortune.warnings" :key="i">{{ warn }}</li>
                </ul>
              </div>

              <div class="advice-box">
                <h4>年度建議</h4>
                <p>{{ yearlyFortune.advice }}</p>
              </div>
            </div>
          </template>
          <div v-else class="loading-state">
            <sl-spinner></sl-spinner>
          </div>
        </div>
      </section>

      <!-- Match Tab -->
      <section v-if="activeMainTab === 'match'" class="match-tab">
        <div class="sub-tabs">
          <button
            class="pill-btn"
            :class="{ active: activeMatchTab === 'finder' }"
            @click="activeMatchTab = 'finder'"
          >尋找配對</button>
          <button
            class="pill-btn"
            :class="{ active: activeMatchTab === 'compat' }"
            @click="activeMatchTab = 'compat'"
          >相性診斷</button>
          <button
            class="pill-btn"
            :class="{ active: activeMatchTab === 'partners' }"
            @click="activeMatchTab = 'partners'"
          >我的配對</button>
        </div>

        <!-- Finder -->
        <div v-if="activeMatchTab === 'finder'" class="match-content">
          <template v-if="compatFinder">
            <div class="relation-grid">
              <div
                v-for="rk in relationKeys"
                :key="rk.key"
                class="relation-section"
                :class="rk.cssClass"
              >
                <h4 class="relation-title">
                  {{ (compatFinder as any)[rk.key]?.relation }}
                  <span class="relation-score">{{ (compatFinder as any)[rk.key]?.score }} 分</span>
                </h4>
                <p class="relation-desc">{{ (compatFinder as any)[rk.key]?.description }}</p>
                <div class="mansion-chips">
                  <button
                    v-for="m in (compatFinder as any)[rk.key]?.mansions"
                    :key="m.index"
                    class="mansion-chip"
                    :class="{ active: selectedMansion?.index === m.index }"
                    @click="selectedMansion = selectedMansion?.index === m.index ? null : m"
                  >
                    {{ m.name_jp }}
                    <span class="chip-element" :style="{ background: elementColors[m.element] }">{{ m.element }}</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Selected Mansion Detail -->
            <div v-if="selectedMansion" class="mansion-detail">
              <h4>{{ selectedMansion.name_jp }}（{{ selectedMansion.reading }}）</h4>
              <p>{{ selectedMansion.personality }}</p>
              <div class="keywords">
                <span v-for="kw in selectedMansion.keywords" :key="kw" class="keyword">{{ kw }}</span>
              </div>
              <div class="lunar-dates">
                <h5>農曆日期對照</h5>
                <div v-for="ld in selectedMansion.lunar_dates" :key="ld.lunar_month" class="lunar-date">
                  <button class="lunar-toggle" @click="toggleLunarDate(ld)">
                    {{ ld.display }}
                    <sl-icon :name="expandedLunarDates.includes(ld.lunar_month) ? 'chevron-up' : 'chevron-down'"></sl-icon>
                  </button>
                  <div v-if="expandedLunarDates.includes(ld.lunar_month) && ld.solar_dates" class="solar-dates">
                    <span v-for="sd in ld.solar_dates" :key="sd.solar_date" class="solar-date">
                      {{ sd.display }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="loading-state">
            <sl-spinner></sl-spinner>
          </div>
        </div>

        <!-- Compatibility Diagnosis -->
        <div v-if="activeMatchTab === 'compat'" class="match-content">
          <div class="compat-form">
            <sl-input
              type="date"
              v-model="date2"
              label="對方生日"
              :max="new Date().toISOString().split('T')[0]"
            ></sl-input>
            <button
              class="btn-primary"
              :disabled="!date2 || compatLoading"
              @click="calculateCompatibility"
            >
              <sl-spinner v-if="compatLoading"></sl-spinner>
              <span v-else>分析</span>
            </button>
          </div>

          <div v-if="compatError" class="error-msg">{{ compatError }}</div>

          <div v-if="compatibility" class="compat-result">
            <div class="compat-score" :class="getScoreLevel(compatibility.score).class">
              <span class="score-num">{{ compatibility.score }}</span>
              <span class="score-text">{{ getScoreLevel(compatibility.score).text }}</span>
            </div>

            <div class="compat-persons">
              <div class="person-card">
                <h5>你</h5>
                <p class="person-mansion">{{ compatibility.person1.mansion }}</p>
                <span class="person-element">{{ compatibility.person1.element }}</span>
              </div>
              <div class="relation-arrow">
                <span class="relation-name">{{ compatibility.relation.name }}</span>
                <span class="relation-reading">{{ compatibility.relation.reading }}</span>
              </div>
              <div class="person-card">
                <h5>對方</h5>
                <p class="person-mansion">{{ compatibility.person2.mansion }}</p>
                <span class="person-element">{{ compatibility.person2.element }}</span>
              </div>
            </div>

            <div class="compat-detail">
              <p>{{ compatibility.relation.description }}</p>
              <p>{{ compatibility.summary }}</p>
            </div>

            <div class="compat-advice">
              <h5>相處建議</h5>
              <p>{{ compatibility.relation.advice }}</p>
              <div v-if="compatibility.relation.tips?.length" class="tips">
                <h6>小技巧</h6>
                <ul>
                  <li v-for="(tip, i) in compatibility.relation.tips" :key="i">{{ tip }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Partners -->
        <div v-if="activeMatchTab === 'partners'" class="match-content">
          <template v-if="partnersWithBirthDate.length === 0">
            <div class="empty-partners">
              <p>尚未設定收藏對象</p>
              <router-link to="/profile" class="btn-link">前往設定</router-link>
            </div>
          </template>
          <template v-else-if="partnerCompatLoading">
            <div class="loading-state">
              <sl-spinner></sl-spinner>
            </div>
          </template>
          <template v-else>
            <div class="partner-list">
              <div
                v-for="pc in partnerCompatibilities"
                :key="pc.partnerId"
                class="partner-card"
                :class="getScoreClass(pc.score)"
              >
                <div class="partner-info">
                  <span class="partner-name">{{ pc.nickname }}</span>
                  <span class="partner-mansion">{{ pc.mansion.name_jp }}</span>
                </div>
                <div class="partner-relation">
                  <span class="relation-name">{{ pc.relation.name }}</span>
                </div>
                <div class="partner-score">
                  <span class="score-num">{{ pc.score }}</span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </section>

      <!-- Lucky Days Tab -->
      <section v-if="activeMainTab === 'lucky'" class="lucky-tab">
        <div class="lucky-layout">
          <!-- Category Sidebar -->
          <aside class="lucky-sidebar">
            <button
              v-for="cat in luckyDayCategories"
              :key="cat.key"
              class="category-btn"
              :class="{ active: selectedLuckyCategory === cat.key }"
              @click="selectLuckyCategory(cat.key)"
            >
              <sl-icon :name="cat.icon"></sl-icon>
              <span>{{ cat.name }}</span>
            </button>
          </aside>

          <!-- Main Content -->
          <div class="lucky-main">
            <template v-if="selectedLuckyCategory">
              <!-- Action Buttons -->
              <div class="action-btns">
                <button
                  v-for="act in currentCategoryActions"
                  :key="act.key"
                  class="action-btn"
                  :class="{ active: selectedLuckyAction === act.key }"
                  @click="selectLuckyAction(act.key)"
                >{{ act.name }}</button>
              </div>

              <!-- Results -->
              <div v-if="luckyDayLoading" class="loading-state">
                <sl-spinner></sl-spinner>
              </div>
              <div v-else-if="luckyDayResult" class="lucky-results">
                <div class="results-grid">
                  <div class="result-col good">
                    <h4>近 30 天吉日</h4>
                    <div class="day-list">
                      <div
                        v-for="day in luckyDayResult.lucky_days"
                        :key="day.date"
                        class="day-item"
                        :class="getScoreClass(day.score)"
                      >
                        <span class="day-date">{{ formatDate(day.date) }}</span>
                        <span class="day-weekday">{{ day.weekday }}</span>
                        <span class="day-rating">{{ day.rating || getFortuneLevel(day.score).text }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="result-col avoid">
                    <h4>應避開的日期</h4>
                    <div class="day-list">
                      <div
                        v-for="day in luckyDayResult.avoid_days"
                        :key="day.date"
                        class="day-item warning"
                      >
                        <span class="day-date">{{ formatDate(day.date) }}</span>
                        <span class="day-weekday">{{ day.weekday }}</span>
                        <span class="day-reason">{{ day.reason }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="luckyDayResult.advice" class="advice-box">
                  <h4>建議</h4>
                  <p>{{ luckyDayResult.advice }}</p>
                </div>
              </div>
              <div v-else class="select-prompt">
                <p>請選擇要查詢的項目</p>
              </div>
            </template>
            <template v-else>
              <div class="select-prompt">
                <p>請先選擇類別</p>
              </div>
            </template>
          </div>
        </div>
      </section>

      <!-- Knowledge Tab -->
      <section v-if="activeMainTab === 'knowledge'" class="knowledge-tab">
        <div class="sub-tabs scrollable">
          <button
            class="pill-btn"
            :class="{ active: activeKnowledgeTab === 'mansion' }"
            @click="activeKnowledgeTab = 'mansion'"
          >本命宿</button>
          <button
            class="pill-btn"
            :class="{ active: activeKnowledgeTab === 'wheel' }"
            @click="activeKnowledgeTab = 'wheel'"
          >二十七宿</button>
          <button
            class="pill-btn"
            :class="{ active: activeKnowledgeTab === 'relations' }"
            @click="activeKnowledgeTab = 'relations'"
          >六種關係</button>
          <button
            class="pill-btn"
            :class="{ active: activeKnowledgeTab === 'elements' }"
            @click="activeKnowledgeTab = 'elements'"
          >七曜</button>
          <button
            class="pill-btn"
            :class="{ active: activeKnowledgeTab === 'calendar' }"
            @click="activeKnowledgeTab = 'calendar'"
          >傍通曆</button>
          <button
            class="pill-btn"
            :class="{ active: activeKnowledgeTab === 'history' }"
            @click="activeKnowledgeTab = 'history'"
          >歷史</button>
        </div>

        <!-- My Mansion -->
        <div v-if="activeKnowledgeTab === 'mansion'" class="knowledge-content">
          <div class="mansion-info-card">
            <h3>{{ mansion?.name_jp }}（{{ mansion?.reading }}）</h3>
            <p class="mansion-element-text">
              <span class="element-badge" :style="{ background: mansionElementColor }">{{ mansion?.element }}</span>
              元素
            </p>
            <div class="mansion-sections">
              <div class="info-section">
                <h4>性格特質</h4>
                <p>{{ mansion?.personality }}</p>
              </div>
              <div class="info-section">
                <h4>關鍵字</h4>
                <div class="keywords">
                  <span v-for="kw in mansion?.keywords" :key="kw" class="keyword">{{ kw }}</span>
                </div>
              </div>
              <div class="info-section">
                <h4>愛情運</h4>
                <p>{{ mansion?.love }}</p>
              </div>
              <div class="info-section">
                <h4>事業運</h4>
                <p>{{ mansion?.career }}</p>
              </div>
              <div class="info-section">
                <h4>健康運</h4>
                <p>{{ mansion?.health }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Wheel -->
        <div v-if="activeKnowledgeTab === 'wheel'" class="knowledge-content">
          <MansionWheel
            v-if="allMansions.length > 0"
            :mansions="allMansions"
            :selected-index="selectedWheelMansion?.index ?? -1"
            :highlight-index="mansion?.index ?? -1"
            @select="handleWheelSelect"
          />
          <div v-if="selectedWheelMansion" class="wheel-detail">
            <h4>{{ selectedWheelMansion.name_jp }}（{{ selectedWheelMansion.reading }}）</h4>
            <span class="element-badge" :style="{ background: elementColors[selectedWheelMansion.element] }">
              {{ selectedWheelMansion.element }}
            </span>
            <p>{{ selectedWheelMansion.personality }}</p>
          </div>
        </div>

        <!-- Relations -->
        <div v-if="activeKnowledgeTab === 'relations'" class="knowledge-content">
          <div class="relations-list">
            <div
              v-for="rel in allRelations"
              :key="rel.type"
              class="relation-item"
              :class="{ expanded: expandedRelation === rel.type }"
            >
              <button class="relation-header" @click="toggleRelation(rel.type)">
                <span class="relation-name">{{ rel.name }}（{{ rel.reading }}）</span>
                <span class="relation-score">{{ rel.score }} 分</span>
                <sl-icon :name="expandedRelation === rel.type ? 'chevron-up' : 'chevron-down'"></sl-icon>
              </button>
              <div v-if="expandedRelation === rel.type" class="relation-body">
                <p>{{ rel.description }}</p>
                <p>{{ rel.detailed }}</p>
                <div v-if="rel.good_for?.length" class="good-for">
                  <h5>適合</h5>
                  <ul>
                    <li v-for="(g, i) in rel.good_for" :key="i">{{ g }}</li>
                  </ul>
                </div>
                <div v-if="rel.avoid?.length" class="avoid-for">
                  <h5>應避免</h5>
                  <ul>
                    <li v-for="(a, i) in rel.avoid" :key="i">{{ a }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Elements -->
        <div v-if="activeKnowledgeTab === 'elements'" class="knowledge-content">
          <div class="elements-grid">
            <div
              v-for="el in allElements"
              :key="el.name"
              class="element-card"
              :style="{ borderColor: elementColors[el.name] }"
            >
              <div class="element-header" :style="{ background: elementColors[el.name] }">
                <span class="element-name">{{ el.name }}曜</span>
                <span class="element-reading">{{ el.reading }}</span>
              </div>
              <div class="element-body">
                <p class="planet">{{ el.planet }}</p>
                <p class="traits">{{ el.traits }}</p>
                <p class="energy">{{ el.energy }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Calendar -->
        <div v-if="activeKnowledgeTab === 'calendar'" class="knowledge-content">
          <div class="calendar-info">
            <h3>月宿傍通曆</h3>
            <p>宿曜道使用的是「月宿傍通曆」，根據農曆月份和日期來對應二十七宿。</p>
            <p>每個農曆日期對應一個特定的「宿」，這個對應關係是固定的，不會因年份而改變。</p>
            <div class="calendar-table">
              <table>
                <thead>
                  <tr>
                    <th>農曆月</th>
                    <th>1日</th>
                    <th>2日</th>
                    <th>3日</th>
                    <th>...</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>正月</td>
                    <td>室</td>
                    <td>壁</td>
                    <td>奎</td>
                    <td>...</td>
                  </tr>
                  <tr>
                    <td>二月</td>
                    <td>奎</td>
                    <td>婁</td>
                    <td>胃</td>
                    <td>...</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- History -->
        <div v-if="activeKnowledgeTab === 'history'" class="knowledge-content">
          <div class="history-info" v-if="metadata">
            <h3>{{ metadata.name }}（{{ metadata.reading }}）</h3>
            <div class="history-sections">
              <div class="history-item">
                <h4>起源</h4>
                <p>{{ metadata.origin }}（{{ metadata.origin_reading }}）</p>
              </div>
              <div class="history-item">
                <h4>傳承者</h4>
                <p>{{ metadata.founder }}（{{ metadata.founder_reading }}）</p>
              </div>
              <div class="history-item">
                <h4>典籍</h4>
                <p>{{ metadata.scripture }}（{{ metadata.scripture_reading }}）</p>
              </div>
              <div class="history-item">
                <h4>核心方法</h4>
                <p>{{ metadata.method }}（{{ metadata.method_reading }}）</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* ============================================================================
   Design System - CSS Variables
   ============================================================================ */
.sukuyodo-v2 {
  --bg-primary: #1c1917;
  --bg-surface: #292524;
  --bg-elevated: #44403c;
  --border: #57534e;
  --text-primary: #fafaf9;
  --text-secondary: #a8a29e;
  --accent: #f59e0b;
  --accent-hover: #d97706;
  --success: #22c55e;
  --warning: #ef4444;
  --info: #3b82f6;

  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  --font-xs: 12px;
  --font-sm: 14px;
  --font-base: 16px;
  --font-lg: 18px;
  --font-xl: 24px;

  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  padding: var(--space-md);
}

/* ============================================================================
   Header
   ============================================================================ */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: var(--space-lg);
}

.header-title {
  font-size: var(--font-xl);
  font-weight: 700;
  color: var(--accent);
  margin: 0;
}

.header-title rt {
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

.btn-query {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-query:hover {
  background: var(--bg-elevated);
  border-color: var(--accent);
}

/* ============================================================================
   Query Dialog
   ============================================================================ */
.query-dialog::part(panel) {
  background: var(--bg-surface);
  border: 1px solid var(--border);
}

.query-dialog::part(title) {
  color: var(--accent);
}

.query-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.query-desc {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  margin: 0;
}

.quick-select {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-sm);
}

.quick-label {
  color: var(--text-secondary);
  font-size: var(--font-sm);
}

.quick-btns {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.quick-btn {
  padding: var(--space-xs) var(--space-sm);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: var(--font-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover,
.quick-btn.active {
  background: var(--accent);
  color: var(--bg-primary);
  border-color: var(--accent);
}

.query-form sl-input {
  --sl-input-background-color: var(--bg-elevated);
  --sl-input-border-color: var(--border);
  --sl-input-color: var(--text-primary);
  --sl-input-label-color: var(--text-secondary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

.error-msg {
  color: var(--warning);
  font-size: var(--font-sm);
  padding: var(--space-sm);
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-sm);
}

/* ============================================================================
   Summary Card
   ============================================================================ */
.summary-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-lg);
  background: linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-primary) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-lg);
}

.summary-main {
  flex: 1;
}

.summary-mansion {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.mansion-star {
  color: var(--accent);
  font-size: var(--font-xl);
}

.mansion-name {
  font-size: var(--font-xl);
  font-weight: 700;
  color: var(--accent);
}

.mansion-name rt {
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

.mansion-element {
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  color: var(--bg-primary);
  font-size: var(--font-sm);
  font-weight: 600;
}

.mansion-desc {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  margin: 0 0 var(--space-sm);
}

.mansion-relation {
  font-size: var(--font-sm);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
}

.mansion-relation.excellent { border-left: 3px solid var(--success); }
.mansion-relation.good { border-left: 3px solid var(--accent); }
.mansion-relation.fair { border-left: 3px solid var(--info); }
.mansion-relation.neutral { border-left: 3px solid var(--text-secondary); }
.mansion-relation.caution { border-left: 3px solid #eab308; }
.mansion-relation.warning { border-left: 3px solid var(--warning); }

.summary-fortune {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  min-width: 80px;
}

.fortune-score {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
}

.fortune-score.excellent { color: var(--success); }
.fortune-score.good { color: var(--accent); }
.fortune-score.fair { color: var(--info); }
.fortune-score.caution { color: #eab308; }
.fortune-score.warning { color: var(--warning); }

.fortune-label {
  color: var(--text-secondary);
  font-size: var(--font-xs);
}

.fortune-level {
  font-size: var(--font-sm);
  font-weight: 600;
}

.fortune-level.excellent { color: var(--success); }
.fortune-level.good { color: var(--accent); }
.fortune-level.fair { color: var(--info); }
.fortune-level.caution { color: #eab308; }
.fortune-level.warning { color: var(--warning); }

/* ============================================================================
   Empty State
   ============================================================================ */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl);
  text-align: center;
}

.empty-state sl-icon {
  font-size: 64px;
  color: var(--accent);
  margin-bottom: var(--space-lg);
}

.empty-state h2 {
  font-size: var(--font-lg);
  margin: 0 0 var(--space-sm);
}

.empty-state p {
  color: var(--text-secondary);
  margin: 0 0 var(--space-lg);
}

.btn-primary {
  padding: var(--space-sm) var(--space-lg);
  background: var(--accent);
  border: none;
  border-radius: var(--radius-md);
  color: var(--bg-primary);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: var(--accent-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============================================================================
   Main Tabs
   ============================================================================ */
.main-tabs {
  display: flex;
  gap: var(--space-sm);
  border-bottom: 1px solid var(--border);
  margin-bottom: var(--space-lg);
}

.tab-btn {
  padding: var(--space-sm) var(--space-md);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  font-size: var(--font-base);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

/* ============================================================================
   Sub Tabs (Pills)
   ============================================================================ */
.sub-tabs {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.sub-tabs.scrollable {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.sub-tabs.scrollable::-webkit-scrollbar {
  display: none;
}

.pill-btn {
  padding: var(--space-sm) var(--space-md);
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: var(--font-sm);
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
}

.pill-btn:hover {
  border-color: var(--accent);
  color: var(--text-primary);
}

.pill-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--bg-primary);
}

/* ============================================================================
   Fortune Tab
   ============================================================================ */
.fortune-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.fortune-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.fortune-title {
  font-size: var(--font-lg);
  margin: 0 0 var(--space-lg);
  color: var(--text-primary);
}

.weekday-element,
.date-range,
.year-info {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  font-weight: 400;
}

.score-bars {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.score-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.score-label {
  width: 48px;
  color: var(--text-secondary);
  font-size: var(--font-sm);
}

.score-bar {
  flex: 1;
  height: 8px;
  background: var(--bg-elevated);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: var(--radius-sm);
  transition: width 0.5s ease;
}

.score-fill.excellent { background: var(--success); }
.score-fill.good { background: var(--accent); }
.score-fill.fair { background: var(--info); }
.score-fill.caution { background: #eab308; }
.score-fill.warning { background: var(--warning); }

.score-value {
  width: 32px;
  text-align: right;
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.lucky-info {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-lg);
  padding: var(--space-md);
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-lg);
}

.lucky-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.lucky-label {
  color: var(--text-secondary);
  font-size: var(--font-xs);
}

.lucky-value {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--font-sm);
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.advice-box {
  padding: var(--space-md);
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--accent);
}

.advice-box h4 {
  font-size: var(--font-sm);
  color: var(--accent);
  margin: 0 0 var(--space-sm);
}

.advice-box p {
  margin: 0;
  font-size: var(--font-sm);
  color: var(--text-secondary);
  line-height: 1.6;
}

.theme-box {
  padding: var(--space-md);
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-lg);
}

.theme-box h4 {
  color: var(--accent);
  margin: 0 0 var(--space-xs);
}

.theme-box p {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  margin: 0;
}

.daily-overview,
.weekly-overview {
  margin-bottom: var(--space-lg);
}

.daily-overview h4,
.weekly-overview h4 {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-sm);
}

.daily-list {
  display: flex;
  gap: var(--space-sm);
  overflow-x: auto;
  padding-bottom: var(--space-sm);
}

.daily-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm);
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  min-width: 60px;
}

.daily-item.excellent { border-bottom: 2px solid var(--success); }
.daily-item.good { border-bottom: 2px solid var(--accent); }
.daily-item.fair { border-bottom: 2px solid var(--info); }
.daily-item.caution { border-bottom: 2px solid #eab308; }
.daily-item.warning { border-bottom: 2px solid var(--warning); }

.day-date {
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

.day-weekday {
  font-size: var(--font-sm);
}

.day-score {
  font-size: var(--font-lg);
  font-weight: 600;
}

.weekly-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.weekly-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.week-num {
  width: 60px;
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.week-bar {
  flex: 1;
  height: 8px;
  background: var(--bg-elevated);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.week-fill {
  height: 100%;
  border-radius: var(--radius-sm);
}

.week-fill.excellent { background: var(--success); }
.week-fill.good { background: var(--accent); }
.week-fill.fair { background: var(--info); }
.week-fill.caution { background: #eab308; }
.week-fill.warning { background: var(--warning); }

.week-score {
  width: 32px;
  text-align: right;
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.opportunities,
.warnings {
  margin-bottom: var(--space-lg);
}

.opportunities h4 {
  color: var(--success);
  font-size: var(--font-sm);
  margin: 0 0 var(--space-sm);
}

.warnings h4 {
  color: var(--warning);
  font-size: var(--font-sm);
  margin: 0 0 var(--space-sm);
}

.opportunities ul,
.warnings ul {
  margin: 0;
  padding-left: var(--space-lg);
}

.opportunities li,
.warnings li {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-xs);
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: var(--space-2xl);
}

/* ============================================================================
   Match Tab
   ============================================================================ */
.match-content {
  animation: fadeIn 0.3s ease;
}

.relation-grid {
  display: grid;
  gap: var(--space-md);
}

.relation-section {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
}

.relation-section.excellent { border-left: 3px solid var(--success); }
.relation-section.good { border-left: 3px solid var(--accent); }
.relation-section.fair { border-left: 3px solid var(--info); }
.relation-section.neutral { border-left: 3px solid var(--text-secondary); }
.relation-section.caution { border-left: 3px solid #eab308; }
.relation-section.warning { border-left: 3px solid var(--warning); }

.relation-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-base);
  margin: 0 0 var(--space-xs);
}

.relation-score {
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.relation-desc {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-sm);
}

.mansion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.mansion-chip {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  color: var(--text-primary);
  font-size: var(--font-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.mansion-chip:hover {
  border-color: var(--accent);
}

.mansion-chip.active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--bg-primary);
}

.chip-element {
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--font-xs);
  color: var(--bg-primary);
}

.mansion-detail {
  margin-top: var(--space-lg);
  padding: var(--space-lg);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.mansion-detail h4 {
  font-size: var(--font-lg);
  margin: 0 0 var(--space-sm);
}

.mansion-detail p {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  margin: 0 0 var(--space-md);
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  margin-bottom: var(--space-md);
}

.keyword {
  padding: var(--space-xs) var(--space-sm);
  background: var(--bg-elevated);
  border-radius: var(--radius-sm);
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

.lunar-dates h5 {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-sm);
}

.lunar-date {
  margin-bottom: var(--space-xs);
}

.lunar-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: var(--space-sm);
  background: var(--bg-elevated);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--font-sm);
  cursor: pointer;
}

.solar-dates {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  padding: var(--space-sm);
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  margin-top: var(--space-xs);
}

.solar-date {
  padding: var(--space-xs) var(--space-sm);
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

/* Compatibility Form */
.compat-form {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.compat-form sl-input {
  flex: 1;
  --sl-input-background-color: var(--bg-surface);
  --sl-input-border-color: var(--border);
  --sl-input-color: var(--text-primary);
  --sl-input-label-color: var(--text-secondary);
}

.compat-result {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.compat-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.compat-score .score-num {
  font-size: 64px;
  font-weight: 700;
  line-height: 1;
}

.compat-score .score-text {
  font-size: var(--font-lg);
  margin-top: var(--space-sm);
}

.compat-score.excellent .score-num,
.compat-score.excellent .score-text { color: var(--success); }
.compat-score.good .score-num,
.compat-score.good .score-text { color: var(--accent); }
.compat-score.fair .score-num,
.compat-score.fair .score-text { color: var(--info); }
.compat-score.warning .score-num,
.compat-score.warning .score-text { color: var(--warning); }

.compat-persons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.person-card {
  text-align: center;
  padding: var(--space-md);
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  min-width: 100px;
}

.person-card h5 {
  margin: 0 0 var(--space-xs);
  color: var(--text-secondary);
  font-size: var(--font-sm);
}

.person-mansion {
  font-size: var(--font-lg);
  font-weight: 600;
  margin: 0 0 var(--space-xs);
}

.person-element {
  padding: var(--space-xs) var(--space-sm);
  background: var(--accent);
  border-radius: var(--radius-sm);
  color: var(--bg-primary);
  font-size: var(--font-xs);
}

.relation-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.relation-arrow .relation-name {
  font-size: var(--font-lg);
  font-weight: 600;
  color: var(--accent);
}

.relation-arrow .relation-reading {
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.compat-detail {
  margin-bottom: var(--space-lg);
}

.compat-detail p {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  line-height: 1.6;
  margin: 0 0 var(--space-sm);
}

.compat-advice h5 {
  color: var(--accent);
  font-size: var(--font-base);
  margin: 0 0 var(--space-sm);
}

.compat-advice p {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  line-height: 1.6;
  margin: 0 0 var(--space-md);
}

.tips h6 {
  color: var(--text-primary);
  font-size: var(--font-sm);
  margin: 0 0 var(--space-xs);
}

.tips ul {
  margin: 0;
  padding-left: var(--space-lg);
}

.tips li {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  margin-bottom: var(--space-xs);
}

/* Partners */
.empty-partners {
  text-align: center;
  padding: var(--space-2xl);
}

.empty-partners p {
  color: var(--text-secondary);
  margin-bottom: var(--space-md);
}

.btn-link {
  color: var(--accent);
  text-decoration: none;
}

.btn-link:hover {
  text-decoration: underline;
}

.partner-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.partner-card {
  display: flex;
  align-items: center;
  padding: var(--space-md);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
}

.partner-card.excellent { border-left: 3px solid var(--success); }
.partner-card.good { border-left: 3px solid var(--accent); }
.partner-card.fair { border-left: 3px solid var(--info); }
.partner-card.caution { border-left: 3px solid #eab308; }
.partner-card.warning { border-left: 3px solid var(--warning); }

.partner-info {
  flex: 1;
}

.partner-name {
  display: block;
  font-weight: 600;
  margin-bottom: var(--space-xs);
}

.partner-mansion {
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.partner-relation {
  padding: 0 var(--space-md);
}

.partner-relation .relation-name {
  color: var(--accent);
  font-size: var(--font-sm);
}

.partner-score .score-num {
  font-size: var(--font-xl);
  font-weight: 700;
}

/* ============================================================================
   Lucky Days Tab
   ============================================================================ */
.lucky-layout {
  display: flex;
  gap: var(--space-lg);
}

.lucky-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  min-width: 160px;
}

.category-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-surface);
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--font-sm);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.category-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.category-btn.active {
  background: var(--accent);
  color: var(--bg-primary);
}

.lucky-main {
  flex: 1;
}

.action-btns {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.action-btn {
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: var(--font-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: var(--accent);
  color: var(--text-primary);
}

.action-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--bg-primary);
}

.lucky-results {
  animation: fadeIn 0.3s ease;
}

.results-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.result-col h4 {
  font-size: var(--font-sm);
  margin: 0 0 var(--space-sm);
}

.result-col.good h4 { color: var(--success); }
.result-col.avoid h4 { color: var(--warning); }

.day-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.day-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm);
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
}

.day-item.excellent { border-left: 3px solid var(--success); }
.day-item.good { border-left: 3px solid var(--accent); }
.day-item.fair { border-left: 3px solid var(--info); }
.day-item.caution { border-left: 3px solid #eab308; }
.day-item.warning { border-left: 3px solid var(--warning); }

.day-rating {
  margin-left: auto;
  font-size: var(--font-sm);
  color: var(--success);
}

.day-reason {
  margin-left: auto;
  font-size: var(--font-sm);
  color: var(--warning);
}

.select-prompt {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: var(--space-2xl);
  color: var(--text-secondary);
}

/* ============================================================================
   Knowledge Tab
   ============================================================================ */
.knowledge-content {
  animation: fadeIn 0.3s ease;
}

.mansion-info-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.mansion-info-card h3 {
  font-size: var(--font-xl);
  color: var(--accent);
  margin: 0 0 var(--space-sm);
}

.mansion-element-text {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-lg);
}

.element-badge {
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  color: var(--bg-primary);
  font-weight: 600;
}

.mansion-sections {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.info-section h4 {
  font-size: var(--font-sm);
  color: var(--accent);
  margin: 0 0 var(--space-sm);
}

.info-section p {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  line-height: 1.6;
  margin: 0;
}

.wheel-detail {
  margin-top: var(--space-lg);
  padding: var(--space-lg);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  text-align: center;
}

.wheel-detail h4 {
  margin: 0 0 var(--space-sm);
}

.wheel-detail p {
  color: var(--text-secondary);
  margin: var(--space-sm) 0 0;
}

.relations-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.relation-item {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.relation-header {
  display: flex;
  align-items: center;
  width: 100%;
  padding: var(--space-md);
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
}

.relation-header .relation-name {
  flex: 1;
  text-align: left;
  font-weight: 600;
}

.relation-header .relation-score {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  margin-right: var(--space-sm);
}

.relation-body {
  padding: var(--space-md);
  border-top: 1px solid var(--border);
  background: var(--bg-elevated);
}

.relation-body p {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  line-height: 1.6;
  margin: 0 0 var(--space-sm);
}

.good-for h5,
.avoid-for h5 {
  font-size: var(--font-sm);
  margin: var(--space-md) 0 var(--space-xs);
}

.good-for h5 { color: var(--success); }
.avoid-for h5 { color: var(--warning); }

.good-for ul,
.avoid-for ul {
  margin: 0;
  padding-left: var(--space-lg);
}

.good-for li,
.avoid-for li {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-xs);
}

.elements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-md);
}

.element-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.element-header {
  padding: var(--space-sm) var(--space-md);
  color: var(--bg-primary);
}

.element-name {
  font-weight: 600;
  margin-right: var(--space-sm);
}

.element-reading {
  font-size: var(--font-sm);
  opacity: 0.8;
}

.element-body {
  padding: var(--space-md);
}

.element-body .planet {
  font-weight: 600;
  margin: 0 0 var(--space-xs);
}

.element-body .traits,
.element-body .energy {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  margin: 0 0 var(--space-xs);
}

.calendar-info,
.history-info {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.calendar-info h3,
.history-info h3 {
  color: var(--accent);
  margin: 0 0 var(--space-md);
}

.calendar-info p,
.history-info p {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  line-height: 1.6;
  margin: 0 0 var(--space-md);
}

.calendar-table {
  overflow-x: auto;
}

.calendar-table table {
  width: 100%;
  border-collapse: collapse;
}

.calendar-table th,
.calendar-table td {
  padding: var(--space-sm);
  border: 1px solid var(--border);
  text-align: center;
  font-size: var(--font-sm);
}

.calendar-table th {
  background: var(--bg-elevated);
  color: var(--text-secondary);
}

.history-sections {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.history-item h4 {
  font-size: var(--font-sm);
  color: var(--accent);
  margin: 0 0 var(--space-xs);
}

.history-item p {
  margin: 0;
}

/* ============================================================================
   Responsive
   ============================================================================ */
@media (max-width: 768px) {
  .sukuyodo-v2 {
    padding: var(--space-sm);
  }

  .header {
    flex-direction: column;
    gap: var(--space-md);
    text-align: center;
  }

  .summary-card {
    flex-direction: column;
    text-align: center;
    gap: var(--space-lg);
  }

  .summary-fortune {
    flex-direction: row;
    gap: var(--space-md);
  }

  .main-tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  .main-tabs::-webkit-scrollbar {
    display: none;
  }

  .lucky-layout {
    flex-direction: column;
  }

  .lucky-sidebar {
    flex-direction: row;
    overflow-x: auto;
    min-width: auto;
    -webkit-overflow-scrolling: touch;
  }

  .category-btn {
    white-space: nowrap;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }

  .compat-persons {
    flex-direction: column;
  }

  .relation-arrow {
    transform: rotate(90deg);
    margin: var(--space-sm) 0;
  }

  .elements-grid {
    grid-template-columns: 1fr;
  }
}
</style>
