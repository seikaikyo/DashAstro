<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'

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

const route = useRoute()
const horoscope = ref<WeeklyHoroscope | null>(null)
const loading = ref(true)
const error = ref('')

const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'

const code = computed(() => route.params.code as string)

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
})

const scoreStars = (score: number | null) => {
  if (!score) return ''
  return '&#9733;'.repeat(score) + '&#9734;'.repeat(5 - score)
}
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
</style>
