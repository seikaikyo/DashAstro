<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiUrl } from '@/config/api'

interface ZodiacSign {
  id: number
  code: string
  name_zh: string
  name_en: string
  symbol: string
  element: string
  element_zh: string
  date_start: string
  date_end: string
}

const signs = ref<ZodiacSign[]>([])
const loading = ref(true)
const error = ref('')

const elementColors: Record<string, string> = {
  fire: '#E85D4C',
  earth: '#8B7355',
  air: '#7CB3D9',
  water: '#5B8FA8'
}

onMounted(async () => {
  try {
    const res = await fetch(`${apiUrl}/api/horoscope/zodiac`)
    if (res.ok) {
      signs.value = await res.json()
    } else {
      error.value = '無法載入星座資料'
    }
  } catch (e) {
    error.value = '無法連線到伺服器'
  } finally {
    loading.value = false
  }
})

const formatDateRange = (start: string, end: string) => {
  const [sm, sd] = start.split('-')
  const [em, ed] = end.split('-')
  return `${parseInt(sm)}/${parseInt(sd)} - ${parseInt(em)}/${parseInt(ed)}`
}
</script>

<template>
  <div class="horoscope-page">
    <div class="container">
      <header class="page-header">
        <h1>星座運勢</h1>
        <p>選擇你的星座，查看本週運勢</p>
      </header>

      <div v-if="loading" class="loading" aria-live="polite" aria-busy="true">
        <sl-spinner style="font-size: 2rem;"></sl-spinner>
        <p>載入中...</p>
      </div>

      <div v-else-if="error" class="error">
        <sl-alert variant="danger" open>
          <sl-icon slot="icon" name="exclamation-triangle"></sl-icon>
          {{ error }}
        </sl-alert>
      </div>

      <div v-else class="zodiac-grid">
        <router-link
          v-for="sign in signs"
          :key="sign.code"
          :to="`/horoscope/${sign.code}`"
          class="zodiac-card"
          :style="{ '--element-color': elementColors[sign.element] }"
        >
          <div class="zodiac-symbol">{{ sign.symbol }}</div>
          <h3 class="zodiac-name">{{ sign.name_zh }}</h3>
          <p class="zodiac-date">{{ formatDateRange(sign.date_start, sign.date_end) }}</p>
          <span class="zodiac-element">{{ sign.element_zh }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  text-align: center;
  margin-bottom: var(--space-10);
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

.loading p {
  margin-top: var(--space-4);
  color: var(--text-secondary);
}

.zodiac-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-4);
}

.zodiac-card {
  background: var(--cosmos-dusk);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  text-align: center;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.zodiac-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--element-color);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.zodiac-card:hover {
  border-color: var(--border-gold);
  transform: translateY(-4px);
}

.zodiac-card:hover::before {
  opacity: 1;
}

.zodiac-symbol {
  font-size: 2.5rem;
  margin-bottom: var(--space-3);
}

.zodiac-name {
  font-size: 1.1rem;
  margin-bottom: var(--space-1);
  color: var(--text-primary);
}

.zodiac-date {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}

.zodiac-element {
  display: inline-block;
  font-size: 0.7rem;
  padding: var(--space-1) var(--space-2);
  background: var(--cosmos-twilight);
  border-radius: var(--radius-sm);
  color: var(--element-color);
}
</style>
