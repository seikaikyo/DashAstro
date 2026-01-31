<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useProfile, ZODIAC_SIGNS } from '../stores/profile'
import { apiUrl } from '@/config/api'

interface TarotSpread {
  id: number
  code: string
  name_zh: string
  description: string
  card_count: number
  suitable_questions: string[]
}

const router = useRouter()
const { profile, isProfileSet, primaryPartner, getPartnerZodiac } = useProfile()

const spreads = ref<TarotSpread[]>([])
const selectedSpread = ref<string>('single')
const question = ref('')
const includeCompatibility = ref(true)
const loading = ref(true)
const drawing = ref(false)

onMounted(async () => {
  try {
    const res = await fetch(`${apiUrl}/api/tarot/spreads`)
    if (res.ok) {
      spreads.value = await res.json()
    }
  } catch (e) {
    console.error('無法載入牌陣資料')
  } finally {
    loading.value = false
  }
})

// 判斷問題是否與感情相關
const isRelationshipQuestion = computed(() => {
  const keywords = ['感情', '愛情', '戀愛', '對象', '另一半', '交往', '關係', '喜歡', '曖昧', '復合', '分手']
  return keywords.some(kw => question.value.includes(kw))
})

// 是否顯示配對選項
const showCompatibilityOption = computed(() => {
  return isProfileSet.value && primaryPartner.value && isRelationshipQuestion.value
})

const myZodiacName = computed(() => {
  return ZODIAC_SIGNS.find(z => z.code === profile.value.zodiacCode)?.name || ''
})

const partnerName = computed(() => {
  if (!primaryPartner.value) return ''
  return primaryPartner.value.nickname || getPartnerZodiac(primaryPartner.value)?.name || ''
})

const drawCards = async () => {
  drawing.value = true
  try {
    const body: any = {
      spread_code: selectedSpread.value,
      question: question.value || null
    }

    // 加入配對資訊
    if (includeCompatibility.value && isProfileSet.value && primaryPartner.value && isRelationshipQuestion.value) {
      body.compatibility = {
        user_zodiac: profile.value.zodiacCode,
        user_gender: profile.value.gender,
        partner_zodiac: primaryPartner.value.zodiacCode,
        partner_gender: primaryPartner.value.gender,
        partner_nickname: primaryPartner.value.nickname
      }
    }

    const res = await fetch(`${apiUrl}/api/tarot/draw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

    if (res.ok) {
      const reading = await res.json()
      // 將配對資訊存到 sessionStorage 供解讀頁使用
      if (body.compatibility) {
        sessionStorage.setItem(`tarot_compat_${reading.id}`, JSON.stringify(body.compatibility))
      }
      router.push(`/tarot/reading/${reading.id}`)
    }
  } catch (e) {
    console.error('抽牌失敗')
  } finally {
    drawing.value = false
  }
}
</script>

<template>
  <div class="tarot-page">
    <div class="container">
      <header class="page-header">
        <h1>塔羅占卜</h1>
        <p>專注於你的問題，讓牌卡揭示指引</p>
      </header>

      <div class="tarot-form card card-gold">
        <div class="form-section">
          <label class="form-label">選擇牌陣</label>
          <div class="spread-options">
            <label
              v-for="spread in spreads"
              :key="spread.code"
              :class="['spread-option', { selected: selectedSpread === spread.code }]"
            >
              <input
                type="radio"
                :value="spread.code"
                v-model="selectedSpread"
                class="sr-only"
              />
              <span class="spread-count">{{ spread.card_count }} 張</span>
              <span class="spread-name">{{ spread.name_zh }}</span>
              <span class="spread-desc">{{ spread.description }}</span>
            </label>
          </div>
        </div>

        <div class="form-section">
          <label class="form-label">你的問題（選填）</label>
          <sl-textarea
            v-model="question"
            name="tarot-question"
            placeholder="例如：我的感情會有什麼發展？"
            rows="3"
            autocomplete="off"
          ></sl-textarea>
          <p class="form-hint">專注於一個具體的問題，會得到更準確的指引</p>
        </div>

        <!-- 配對分析選項 -->
        <div v-if="showCompatibilityOption" class="compat-option">
          <label class="compat-toggle">
            <input type="checkbox" v-model="includeCompatibility" />
            <span class="toggle-text">
              加入配對分析
              <span class="toggle-desc">
                ({{ myZodiacName }} &times; {{ partnerName }})
              </span>
            </span>
          </label>
        </div>

        <!-- 未設定檔案提示 -->
        <div v-else-if="!isProfileSet && isRelationshipQuestion" class="setup-hint">
          <router-link to="/profile">
            <sl-icon name="person-plus"></sl-icon>
            設定我的資料，獲得專屬配對解讀
          </router-link>
        </div>

        <button
          class="btn-gold draw-btn"
          @click="drawCards"
          :disabled="drawing"
          :aria-busy="drawing"
        >
          <sl-spinner v-if="drawing"></sl-spinner>
          <span v-else>開始抽牌</span>
        </button>
      </div>

      <section class="tarot-intro">
        <h2>關於塔羅占卜</h2>
        <div class="intro-grid">
          <div class="intro-item">
            <div class="intro-icon">&#127183;</div>
            <h3>22 張大阿爾克那</h3>
            <p>使用經典的韋特塔羅大牌，每張牌都蘊含深刻的人生智慧</p>
          </div>
          <div class="intro-item">
            <div class="intro-icon">&#129504;</div>
            <h3>AI 智慧解讀</h3>
            <p>結合牌陣位置與你的問題，提供個人化的深度解讀</p>
          </div>
          <div class="intro-item">
            <div class="intro-icon">&#128161;</div>
            <h3>務實建議</h3>
            <p>不只是預測，更提供實用的行動建議和反思方向</p>
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

.tarot-form {
  max-width: 600px;
  margin: 0 auto var(--space-12);
}

.form-section {
  margin-bottom: var(--space-6);
}

.form-label {
  display: block;
  font-weight: 500;
  margin-bottom: var(--space-3);
  color: var(--stellar-gold);
}

.spread-options {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.spread-option {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto auto;
  gap: var(--space-1) var(--space-3);
  padding: var(--space-4);
  background: var(--cosmos-night);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.spread-option:hover {
  border-color: var(--astral-medium);
}

.spread-option.selected {
  border-color: var(--stellar-gold);
  background: var(--cosmos-twilight);
}

.spread-count {
  grid-row: span 2;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--astral-deep);
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--stellar-gold);
}

.spread-name {
  font-weight: 500;
  color: var(--text-primary);
}

.spread-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.form-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: var(--space-2);
}

/* 配對選項 */
.compat-option {
  margin-bottom: var(--space-6);
  padding: var(--space-4);
  background: var(--cosmos-night);
  border: 1px solid var(--border-gold);
  border-radius: var(--radius-md);
}

.compat-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
}

.compat-toggle input {
  width: 18px;
  height: 18px;
  accent-color: var(--stellar-gold);
}

.toggle-text {
  color: var(--text-primary);
}

.toggle-desc {
  color: var(--stellar-gold);
  font-size: 0.9rem;
}

.setup-hint {
  margin-bottom: var(--space-6);
  text-align: center;
}

.setup-hint a {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-muted);
  font-size: 0.9rem;
}

.setup-hint a:hover {
  color: var(--stellar-gold);
}

.draw-btn {
  width: 100%;
  padding: var(--space-4);
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.draw-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.tarot-intro {
  text-align: center;
}

.tarot-intro h2 {
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
</style>
