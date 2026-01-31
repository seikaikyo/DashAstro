<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiUrl } from '@/config/api'

interface MoonPhase {
  phase_name_zh: string
  illumination: number
}

const moonPhase = ref<MoonPhase | null>(null)

onMounted(async () => {
  try {
    const res = await fetch(`${apiUrl}/api/astronomy/moon-phase`)
    if (res.ok) {
      moonPhase.value = await res.json()
    }
  } catch (e) {
    console.error('無法載入月相資料')
  }
})
</script>

<template>
  <div class="home">
    <section class="hero">
      <div class="container">
        <h1 class="hero-title">星語塔羅</h1>
        <p class="hero-subtitle">務實科學的占星分析 + AI 智慧解牌</p>

        <div v-if="moonPhase" class="moon-badge">
          <span class="moon-icon">&#127769;</span>
          <span>今日月相：{{ moonPhase.phase_name_zh }}</span>
          <span class="moon-light">（{{ moonPhase.illumination }}% 亮度）</span>
        </div>

        <div class="hero-actions">
          <router-link to="/horoscope" class="btn-gold">
            查看星座運勢
          </router-link>
          <router-link to="/tarot" class="btn-outline">
            開始塔羅占卜
          </router-link>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="container">
        <div class="feature-grid">
          <router-link to="/horoscope" class="feature-card">
            <div class="feature-icon">&#9733;</div>
            <h3>星座運勢</h3>
            <p>基於真實天文數據的每週運勢分析</p>
          </router-link>

          <router-link to="/tarot" class="feature-card">
            <div class="feature-icon">&#127183;</div>
            <h3>塔羅占卜</h3>
            <p>AI 智慧解牌，提供深度洞察</p>
          </router-link>

          <router-link to="/sky" class="feature-card">
            <div class="feature-icon">&#127761;</div>
            <h3>今日天象</h3>
            <p>即時行星位置、逆行、相位資訊</p>
          </router-link>

          <router-link to="/sukuyodo" class="feature-card sukuyodo-card">
            <div class="feature-icon">&#9764;</div>
            <h3>宿曜道</h3>
            <p>真言宗密教占星術，查詢本命宿與相性</p>
            <span class="card-badge">東方占星</span>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  text-align: center;
  padding: var(--space-12) 0;
  background: linear-gradient(180deg, var(--cosmos-night) 0%, var(--cosmos-void) 100%);
}

.hero-title {
  font-size: 3.5rem;
  margin-bottom: var(--space-4);
  background: linear-gradient(135deg, var(--stellar-gold), var(--stellar-glow));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
}

.moon-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--cosmos-dusk);
  border: 1px solid var(--border-gold);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  margin-bottom: var(--space-8);
}

.moon-icon {
  font-size: 1.25rem;
}

.moon-light {
  color: var(--text-muted);
}

.hero-actions {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  flex-wrap: wrap;
}

.btn-outline {
  background: transparent;
  color: var(--stellar-gold);
  border: 1px solid var(--stellar-gold);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: all var(--transition-normal);
}

.btn-outline:hover {
  background: var(--stellar-gold);
  color: var(--cosmos-void);
}

.features {
  padding: var(--space-12) 0;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
}

.feature-card {
  background: var(--cosmos-dusk);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  text-align: center;
  transition: all var(--transition-normal);
}

.feature-card:hover {
  border-color: var(--border-gold);
  transform: translateY(-4px);
  box-shadow: var(--shadow-gold);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: var(--space-4);
}

.feature-card h3 {
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.sukuyodo-card {
  position: relative;
  background: linear-gradient(135deg, var(--cosmos-dusk) 0%, rgba(139, 69, 19, 0.15) 100%);
  border-color: rgba(205, 133, 63, 0.3);
}

.sukuyodo-card:hover {
  border-color: rgba(205, 133, 63, 0.6);
  box-shadow: 0 0 20px rgba(205, 133, 63, 0.2);
}

.card-badge {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
  background: rgba(205, 133, 63, 0.2);
  color: #cd853f;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(205, 133, 63, 0.4);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }
}
</style>
