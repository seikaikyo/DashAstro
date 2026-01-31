<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { apiUrl } from '@/config/api'

interface DrawnCard {
  card_id: number
  position: number
  position_name: string
  is_reversed: boolean
}

interface TarotReading {
  id: string
  question: string | null
  cards_drawn: DrawnCard[]
  ai_interpretation: string | null
}

interface TarotCard {
  id: number
  number: number
  name_zh: string
  name_en: string
  keywords: string[]
  upright_meaning: string
  reversed_meaning: string
  image_url: string
}

const route = useRoute()
const reading = ref<TarotReading | null>(null)
const cards = ref<Map<number, TarotCard>>(new Map())
const loading = ref(true)
const revealedCards = ref<Set<number>>(new Set())
const interpreting = ref(false)
const interpretError = ref('')

onMounted(async () => {
  try {
    const readingRes = await fetch(`${apiUrl}/api/tarot/readings/${route.params.id}`)
    if (readingRes.ok) {
      reading.value = await readingRes.json()
    }

    const cardsRes = await fetch(`${apiUrl}/api/tarot/cards/major`)
    if (cardsRes.ok) {
      const allCards: TarotCard[] = await cardsRes.json()
      allCards.forEach(card => cards.value.set(card.id, card))
    }
  } catch (e) {
    console.error('載入失敗')
  } finally {
    loading.value = false
  }
})

const getCard = (cardId: number) => cards.value.get(cardId)

const revealCard = (position: number) => {
  revealedCards.value.add(position)
}

const allRevealed = computed(() => {
  if (!reading.value) return false
  return reading.value.cards_drawn.every(dc => revealedCards.value.has(dc.position))
})

// 當所有牌翻開且沒有 AI 解讀時，自動請求解讀
watch(allRevealed, async (revealed) => {
  if (revealed && reading.value && !reading.value.ai_interpretation && !interpreting.value) {
    await requestInterpretation()
  }
})

async function requestInterpretation() {
  if (!reading.value || interpreting.value) return

  interpreting.value = true
  interpretError.value = ''

  try {
    // 從 sessionStorage 取得配對資訊
    const compatData = sessionStorage.getItem(`tarot_compat_${reading.value.id}`)
    const compatibility = compatData ? JSON.parse(compatData) : null

    const res = await fetch(`${apiUrl}/api/tarot/interpret`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reading_id: reading.value.id,
        compatibility: compatibility
      })
    })

    if (res.ok) {
      const data = await res.json()
      if (data.interpretation) {
        reading.value.ai_interpretation = data.interpretation
      } else if (data.message) {
        interpretError.value = data.message
      }
    } else {
      interpretError.value = '解讀服務暫時無法使用'
    }
  } catch (e) {
    interpretError.value = '網路連線失敗'
  } finally {
    interpreting.value = false
  }
}
</script>

<template>
  <div class="reading-page">
    <div class="container">
      <router-link to="/tarot" class="back-link">
        <sl-icon name="arrow-left"></sl-icon>
        重新抽牌
      </router-link>

      <div v-if="loading" class="loading">
        <sl-spinner style="font-size: 2rem;"></sl-spinner>
      </div>

      <div v-else-if="reading" class="reading-content">
        <header class="reading-header">
          <h1>你的牌陣</h1>
          <p v-if="reading.question" class="question">「{{ reading.question }}」</p>
        </header>

        <div class="cards-spread">
          <div
            v-for="drawn in reading.cards_drawn"
            :key="drawn.position"
            :class="['card-slot', { revealed: revealedCards.has(drawn.position) }]"
            @click="revealCard(drawn.position)"
          >
            <div class="card-inner">
              <div class="card-back">
                <div class="card-back-design">&#9733;</div>
                <span class="tap-hint">點擊翻牌</span>
              </div>
              <div
                v-if="getCard(drawn.card_id)"
                :class="['card-front', { reversed: drawn.is_reversed }]"
              >
                <div class="card-image">
                  <span class="card-number">{{ getCard(drawn.card_id)!.number }}</span>
                </div>
                <h3 class="card-name">
                  {{ getCard(drawn.card_id)!.name_zh }}
                  <span v-if="drawn.is_reversed" class="reversed-tag">逆位</span>
                </h3>
                <p class="card-position">{{ drawn.position_name }}</p>
              </div>
            </div>
          </div>
        </div>

        <section v-if="allRevealed" class="interpretation-section">
          <div
            v-for="drawn in reading.cards_drawn"
            :key="drawn.position"
            class="card-detail card"
          >
            <div class="detail-header">
              <span class="position-badge">{{ drawn.position_name }}</span>
              <h3>
                {{ getCard(drawn.card_id)?.name_zh }}
                <span v-if="drawn.is_reversed" class="reversed-tag">逆位</span>
              </h3>
            </div>

            <div class="keywords">
              {{ getCard(drawn.card_id)?.keywords?.join(' · ') }}
            </div>

            <p class="meaning">
              {{
                drawn.is_reversed
                  ? getCard(drawn.card_id)?.reversed_meaning
                  : getCard(drawn.card_id)?.upright_meaning
              }}
            </p>
          </div>

          <!-- AI 解讀區塊 -->
          <div v-if="interpreting" class="ai-loading card card-gold">
            <sl-spinner style="font-size: 1.5rem;"></sl-spinner>
            <p>AI 正在解讀你的牌陣...</p>
          </div>

          <div v-else-if="reading.ai_interpretation" class="ai-interpretation card card-gold">
            <h2>AI 綜合解讀</h2>
            <p class="ai-text">{{ reading.ai_interpretation }}</p>
          </div>

          <div v-else-if="interpretError" class="ai-error card">
            <p>{{ interpretError }}</p>
            <button class="btn-gold retry-btn" @click="requestInterpretation">
              重試
            </button>
          </div>
        </section>

        <p v-else class="reveal-hint">
          點擊卡牌逐一翻開，查看完整解讀
        </p>
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

.reading-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.question {
  color: var(--text-secondary);
  font-style: italic;
  margin-top: var(--space-2);
}

.cards-spread {
  display: flex;
  justify-content: center;
  gap: var(--space-6);
  flex-wrap: wrap;
  margin-bottom: var(--space-8);
  perspective: 1000px;
}

.card-slot {
  width: 140px;
  height: 200px;
  cursor: pointer;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.card-slot.revealed .card-inner {
  transform: rotateY(180deg);
}

.card-back,
.card-front {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.card-back {
  background: linear-gradient(135deg, var(--astral-deep), var(--cosmos-twilight));
  border: 2px solid var(--border-gold);
}

.card-back-design {
  font-size: 3rem;
  color: var(--stellar-gold);
  opacity: 0.5;
}

.tap-hint {
  position: absolute;
  bottom: var(--space-3);
  font-size: 0.75rem;
  color: var(--text-muted);
}

.card-front {
  background: var(--cosmos-dusk);
  border: 2px solid var(--border-default);
  transform: rotateY(180deg);
  padding: var(--space-3);
}

.card-front.reversed {
  border-color: var(--error);
}

.card-image {
  width: 80px;
  height: 100px;
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-2);
}

.card-number {
  font-size: 2rem;
  font-family: var(--font-display);
  color: var(--stellar-gold);
}

.card-name {
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: var(--space-1);
}

.card-position {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.reversed-tag {
  display: inline-block;
  font-size: 0.65rem;
  padding: 2px 6px;
  background: var(--error);
  color: white;
  border-radius: var(--radius-sm);
  margin-left: var(--space-1);
  vertical-align: middle;
}

.reveal-hint {
  text-align: center;
  color: var(--text-muted);
}

.interpretation-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.card-detail {
  padding: var(--space-6);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.position-badge {
  background: var(--astral-deep);
  color: var(--stellar-gold);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
}

.detail-header h3 {
  flex: 1;
}

.keywords {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-bottom: var(--space-4);
  color: var(--text-muted);
  font-size: 0.9rem;
}

.meaning {
  color: var(--text-secondary);
  line-height: 1.7;
}

.ai-loading {
  text-align: center;
  padding: var(--space-8);
}

.ai-loading p {
  margin-top: var(--space-4);
  color: var(--text-secondary);
}

.ai-interpretation {
  padding: var(--space-6);
}

.ai-interpretation h2 {
  color: var(--stellar-gold);
  margin-bottom: var(--space-4);
  text-align: center;
}

.ai-text {
  line-height: 1.8;
  white-space: pre-wrap;
}

.ai-error {
  text-align: center;
  padding: var(--space-6);
}

.ai-error p {
  color: var(--text-muted);
  margin-bottom: var(--space-4);
}

.retry-btn {
  padding: var(--space-2) var(--space-4);
}
</style>
