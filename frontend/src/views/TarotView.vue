<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

interface TarotSpread {
  id: number
  code: string
  name_zh: string
  description: string
  card_count: number
  suitable_questions: string[]
}

const router = useRouter()
const spreads = ref<TarotSpread[]>([])
const selectedSpread = ref<string>('single')
const question = ref('')
const loading = ref(true)
const drawing = ref(false)

const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'

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

const drawCards = async () => {
  drawing.value = true
  try {
    const res = await fetch(`${apiUrl}/api/tarot/draw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        spread_code: selectedSpread.value,
        question: question.value || null
      })
    })

    if (res.ok) {
      const reading = await res.json()
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
            placeholder="例如：我的感情會有什麼發展？"
            rows="3"
          ></sl-textarea>
          <p class="form-hint">專注於一個具體的問題，會得到更準確的指引</p>
        </div>

        <button
          class="btn-gold draw-btn"
          @click="drawCards"
          :disabled="drawing"
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
