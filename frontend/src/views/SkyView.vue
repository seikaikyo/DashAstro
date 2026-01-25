<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Planet {
  planet: string
  name_zh: string
  sign_code: string
  sign_name: string
  degree: number
  longitude: number
}

interface MoonPhase {
  phase_name_zh: string
  illumination: number
  phase_angle: number
}

interface RetroPlanet {
  planet: string
  name_zh: string
}

interface SkySummary {
  datetime: string
  moon_phase: MoonPhase
  retrograde_planets: RetroPlanet[]
  retrograde_count: number
  dominant_element: string
  dominant_element_zh: string
  element_distribution: Record<string, number>
  planet_positions: Planet[]
}

const summary = ref<SkySummary | null>(null)
const loading = ref(true)
const error = ref('')

const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'

onMounted(async () => {
  try {
    const res = await fetch(`${apiUrl}/api/astronomy/summary`)
    if (res.ok) {
      summary.value = await res.json()
    } else {
      error.value = '無法載入天象資料'
    }
  } catch (e) {
    error.value = '無法連線到伺服器'
  } finally {
    loading.value = false
  }
})

const elementColors: Record<string, string> = {
  fire: '#E85D4C',
  earth: '#8B7355',
  air: '#7CB3D9',
  water: '#5B8FA8'
}

const elementNames: Record<string, string> = {
  fire: '火象',
  earth: '土象',
  air: '風象',
  water: '水象'
}
</script>

<template>
  <div class="sky-page">
    <div class="container">
      <header class="page-header">
        <h1>今日天象</h1>
        <p>基於 NASA 星曆資料的即時行星位置</p>
      </header>

      <div v-if="loading" class="loading">
        <sl-spinner style="font-size: 2rem;"></sl-spinner>
      </div>

      <div v-else-if="error" class="error">
        <sl-alert variant="danger" open>
          <sl-icon slot="icon" name="exclamation-triangle"></sl-icon>
          {{ error }}
        </sl-alert>
      </div>

      <div v-else-if="summary" class="sky-content">
        <div class="highlight-cards">
          <div class="highlight-card card">
            <div class="highlight-icon">&#127769;</div>
            <h3>月相</h3>
            <p class="highlight-value">{{ summary.moon_phase.phase_name_zh }}</p>
            <p class="highlight-sub">亮度 {{ summary.moon_phase.illumination }}%</p>
          </div>

          <div class="highlight-card card">
            <div class="highlight-icon">&#128260;</div>
            <h3>逆行行星</h3>
            <p class="highlight-value">
              {{ summary.retrograde_count > 0 ? summary.retrograde_count + ' 顆' : '無' }}
            </p>
            <p v-if="summary.retrograde_count > 0" class="highlight-sub">
              {{ summary.retrograde_planets.map(p => p.name_zh).join('、') }}
            </p>
          </div>

          <div class="highlight-card card">
            <div
              class="highlight-icon"
              :style="{ color: elementColors[summary.dominant_element] }"
            >
              &#9728;
            </div>
            <h3>主導元素</h3>
            <p class="highlight-value">{{ summary.dominant_element_zh }}</p>
            <p class="highlight-sub">能量分布最高</p>
          </div>
        </div>

        <section class="element-section card">
          <h2>元素能量分布</h2>
          <div class="element-bars">
            <div
              v-for="(count, element) in summary.element_distribution"
              :key="element"
              class="element-bar"
            >
              <div class="element-label">
                <span
                  class="element-dot"
                  :style="{ background: elementColors[element] }"
                ></span>
                {{ elementNames[element] }}
              </div>
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :style="{
                    width: (count / 10 * 100) + '%',
                    background: elementColors[element]
                  }"
                ></div>
              </div>
              <span class="element-count">{{ count }}</span>
            </div>
          </div>
        </section>

        <section class="planets-section">
          <h2>行星位置</h2>
          <div class="planets-grid">
            <div
              v-for="planet in summary.planet_positions"
              :key="planet.planet"
              class="planet-card card"
            >
              <div class="planet-name">{{ planet.name_zh }}</div>
              <div class="planet-sign">{{ planet.sign_name }}</div>
              <div class="planet-degree">{{ planet.degree.toFixed(1) }}°</div>
            </div>
          </div>
        </section>

        <p class="data-source">
          資料來源：Skyfield + NASA DE421 星曆<br />
          計算時間：{{ new Date(summary.datetime).toLocaleString('zh-TW') }}
        </p>
      </div>
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

.loading,
.error {
  text-align: center;
  padding: var(--space-12);
}

.highlight-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.highlight-card {
  text-align: center;
  padding: var(--space-6);
}

.highlight-icon {
  font-size: 2.5rem;
  margin-bottom: var(--space-3);
}

.highlight-card h3 {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}

.highlight-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--stellar-gold);
  margin-bottom: var(--space-1);
}

.highlight-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.element-section {
  margin-bottom: var(--space-8);
}

.element-section h2 {
  margin-bottom: var(--space-6);
}

.element-bars {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.element-bar {
  display: grid;
  grid-template-columns: 80px 1fr 40px;
  gap: var(--space-4);
  align-items: center;
}

.element-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.element-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.bar-track {
  height: 8px;
  background: var(--cosmos-twilight);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

.element-count {
  text-align: right;
  color: var(--text-muted);
}

.planets-section h2 {
  margin-bottom: var(--space-6);
}

.planets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-8);
}

.planet-card {
  text-align: center;
  padding: var(--space-4);
}

.planet-name {
  font-weight: 500;
  margin-bottom: var(--space-2);
}

.planet-sign {
  color: var(--stellar-gold);
  font-size: 0.95rem;
  margin-bottom: var(--space-1);
}

.planet-degree {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.data-source {
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.8;
}
</style>
