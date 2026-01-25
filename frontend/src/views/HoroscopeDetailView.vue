<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProfile, ZODIAC_SIGNS, type Partner } from '../stores/profile'
import PartnerSelector from '../components/PartnerSelector.vue'

interface WeeklyHoroscope {
  zodiac_code: string
  zodiac_name: string
  zodiac_symbol: string
  week_start: string
  summary: string
  love_advice: string | null
  career_advice: string | null
  health_advice: string | null
  lucky_day: string | null
  lucky_color: string | null
  lucky_number: number | null
  overall_score: number | null
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

const route = useRoute()
const { profile, isProfileSet, primaryPartner, getPartnerZodiac } = useProfile()

const horoscope = ref<WeeklyHoroscope | null>(null)
const compatibility = ref<CompatibilityResult | null>(null)
const loading = ref(true)
const loadingCompat = ref(false)
const error = ref('')

// 當前選擇的對象
const selectedPartner = ref<Partner | null>(null)

const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'

const code = computed(() => route.params.code as string)

// 判斷是否是用戶自己的星座
const isMyZodiac = computed(() => {
  return isProfileSet.value && profile.value.zodiacCode === code.value.toUpperCase()
})

onMounted(async () => {
  try {
    const res = await fetch(`${apiUrl}/api/horoscope/weekly/${code.value}`)
    if (res.ok) {
      horoscope.value = await res.json()
    } else if (res.status === 404) {
      error.value = '尚無本週運勢資料，請稍後再試'
    } else {
      error.value = '無法載入運勢資料'
    }
  } catch (e) {
    error.value = '無法連線到伺服器'
  } finally {
    loading.value = false
  }

  // 初始化選擇的對象
  if (primaryPartner.value) {
    selectedPartner.value = primaryPartner.value
  }

  // 如果是用戶的星座且有對象，載入配對
  if (isMyZodiac.value && selectedPartner.value) {
    await loadCompatibility()
  }
})

// 監聽選擇的對象變化
watch(selectedPartner, async (newPartner) => {
  if (newPartner && isMyZodiac.value) {
    await loadCompatibility()
  }
})

async function loadCompatibility() {
  if (!profile.value.zodiacCode || !selectedPartner.value) return

  loadingCompat.value = true
  try {
    const res = await fetch(`${apiUrl}/api/compatibility/weekly`, {
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

const scoreStars = (score: number | null) => {
  if (!score) return ''
  return '&#9733;'.repeat(score) + '&#9734;'.repeat(5 - score)
}

const compatScoreStars = (score: number) => {
  const full = Math.floor(score)
  const half = score % 1 >= 0.5 ? 1 : 0
  return '\u2605'.repeat(full) + (half ? '\u2606' : '') + '\u2606'.repeat(5 - full - half)
}

const partnerZodiacName = computed(() => {
  if (!primaryPartner.value) return ''
  return getPartnerZodiac(primaryPartner.value)?.name || ''
})

const partnerZodiacSymbol = computed(() => {
  if (!primaryPartner.value) return ''
  return getPartnerZodiac(primaryPartner.value)?.symbol || ''
})

const myZodiacSymbol = computed(() => {
  return ZODIAC_SIGNS.find(z => z.code === profile.value.zodiacCode)?.symbol || ''
})
</script>

<template>
  <div class="detail-page">
    <div class="container">
      <router-link to="/horoscope" class="back-link">
        <sl-icon name="arrow-left"></sl-icon>
        返回星座列表
      </router-link>

      <div v-if="loading" class="loading">
        <sl-spinner style="font-size: 2rem;"></sl-spinner>
      </div>

      <div v-else-if="error" class="error-state">
        <div class="error-icon">&#128301;</div>
        <h2>{{ error }}</h2>
        <p>本週運勢尚在撰寫中，敬請期待</p>
        <router-link to="/horoscope" class="btn-gold">
          返回星座列表
        </router-link>
      </div>

      <div v-else-if="horoscope" class="horoscope-detail">
        <header class="detail-header">
          <span class="zodiac-symbol">{{ horoscope.zodiac_symbol }}</span>
          <h1>{{ horoscope.zodiac_name }}</h1>
          <p class="week-info">{{ horoscope.week_start }} 當週運勢</p>
          <span v-if="isMyZodiac" class="my-badge">我的星座</span>
        </header>

        <div class="detail-content">
          <section class="summary-section card">
            <h2>本週概要</h2>
            <p>{{ horoscope.summary }}</p>

            <div v-if="horoscope.overall_score" class="score">
              <span>整體運勢</span>
              <span class="stars" v-html="scoreStars(horoscope.overall_score)"></span>
            </div>
          </section>

          <div class="advice-grid">
            <section v-if="horoscope.love_advice" class="advice-card card">
              <div class="advice-icon">&#128151;</div>
              <h3>感情運</h3>
              <p>{{ horoscope.love_advice }}</p>

              <!-- 配對分析 (只在用戶自己的星座顯示) -->
              <div v-if="isMyZodiac && profile.partners.length > 0" class="compat-inline">
                <!-- 對象選擇器 -->
                <PartnerSelector v-model="selectedPartner" />

                <div v-if="selectedPartner && compatibility">
                  <div class="compat-header">
                    <span class="compat-pair">
                      {{ myZodiacSymbol }} &hearts; {{ getPartnerZodiac(selectedPartner)?.symbol }}
                    </span>
                    <span class="compat-score">{{ compatScoreStars(compatibility.overall_score) }}</span>
                  </div>
                  <p class="compat-partner">
                    與{{ selectedPartner.nickname || getPartnerZodiac(selectedPartner)?.name }}的本週互動
                  </p>
                  <p class="compat-advice">{{ compatibility.advice }}</p>
                  <p v-if="compatibility.sky_influence?.influences?.length" class="compat-note">
                    {{ compatibility.sky_influence.influences[0] }}
                  </p>
                </div>

                <div v-else-if="loadingCompat" class="compat-loading">
                  <sl-spinner></sl-spinner>
                </div>
              </div>

              <div v-else-if="isMyZodiac && profile.partners.length === 0" class="compat-prompt">
                <router-link to="/profile">
                  <sl-icon name="plus-circle"></sl-icon>
                  新增關注對象，查看配對分析
                </router-link>
              </div>
            </section>

            <section v-if="horoscope.career_advice" class="advice-card card">
              <div class="advice-icon">&#128188;</div>
              <h3>事業運</h3>
              <p>{{ horoscope.career_advice }}</p>
            </section>

            <section v-if="horoscope.health_advice" class="advice-card card">
              <div class="advice-icon">&#128154;</div>
              <h3>健康運</h3>
              <p>{{ horoscope.health_advice }}</p>
            </section>
          </div>

          <section class="lucky-section card">
            <h2>幸運指南</h2>
            <div class="lucky-grid">
              <div v-if="horoscope.lucky_day" class="lucky-item">
                <span class="lucky-label">幸運日</span>
                <span class="lucky-value">{{ horoscope.lucky_day }}</span>
              </div>
              <div v-if="horoscope.lucky_color" class="lucky-item">
                <span class="lucky-label">幸運色</span>
                <span class="lucky-value">{{ horoscope.lucky_color }}</span>
              </div>
              <div v-if="horoscope.lucky_number" class="lucky-item">
                <span class="lucky-label">幸運數字</span>
                <span class="lucky-value">{{ horoscope.lucky_number }}</span>
              </div>
            </div>
          </section>

          <!-- 設定提示 -->
          <section v-if="!isProfileSet" class="setup-prompt card">
            <sl-icon name="person-plus"></sl-icon>
            <p>設定你的星座，查看專屬配對分析</p>
            <router-link to="/profile" class="btn-gold">
              設定我的資料
            </router-link>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
}

.back-link:hover {
  color: var(--stellar-gold);
}

.loading {
  text-align: center;
  padding: var(--space-12);
}

.error-state {
  text-align: center;
  padding: var(--space-12);
}

.error-icon {
  font-size: 4rem;
  margin-bottom: var(--space-4);
}

.error-state h2 {
  margin-bottom: var(--space-2);
}

.error-state p {
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
}

.detail-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.detail-header .zodiac-symbol {
  font-size: 4rem;
  display: block;
  margin-bottom: var(--space-2);
}

.detail-header h1 {
  margin-bottom: var(--space-2);
}

.week-info {
  color: var(--text-muted);
}

.my-badge {
  display: inline-block;
  margin-top: var(--space-3);
  padding: var(--space-1) var(--space-3);
  background: var(--stellar-gold);
  color: var(--cosmos-night);
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 500;
}

.summary-section {
  margin-bottom: var(--space-6);
}

.summary-section h2 {
  margin-bottom: var(--space-4);
  color: var(--stellar-gold);
}

.score {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-subtle);
}

.stars {
  color: var(--stellar-gold);
  font-size: 1.25rem;
}

.advice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.advice-card {
  text-align: center;
}

.advice-icon {
  font-size: 2rem;
  margin-bottom: var(--space-3);
}

.advice-card h3 {
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.advice-card p {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

/* 配對分析內嵌樣式 */
.compat-inline {
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px dashed var(--border-gold);
  text-align: left;
}

.compat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.compat-pair {
  font-size: 1.25rem;
}

.compat-score {
  color: var(--stellar-gold);
  letter-spacing: 2px;
}

.compat-partner {
  font-weight: 500;
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.compat-advice {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-2);
  white-space: pre-line;
}

.compat-note {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
}

.compat-loading {
  margin-top: var(--space-4);
  text-align: center;
}

.compat-prompt {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px dashed var(--border-default);
}

.compat-prompt a {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  color: var(--text-muted);
  font-size: 0.9rem;
}

.compat-prompt a:hover {
  color: var(--stellar-gold);
}

.lucky-section h2 {
  margin-bottom: var(--space-4);
  color: var(--stellar-gold);
}

.lucky-grid {
  display: flex;
  gap: var(--space-8);
  flex-wrap: wrap;
}

.lucky-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.lucky-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.lucky-value {
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--stellar-gold);
}

/* 設定提示 */
.setup-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6);
  text-align: center;
  margin-top: var(--space-6);
}

.setup-prompt sl-icon {
  font-size: 2rem;
  color: var(--text-muted);
}

.setup-prompt p {
  color: var(--text-secondary);
}

.setup-prompt .btn-gold {
  padding: var(--space-2) var(--space-5);
}
</style>
