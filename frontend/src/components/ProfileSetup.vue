<script setup lang="ts">
import { ref, computed } from 'vue'
import { useProfile, ZODIAC_SIGNS, GENDER_OPTIONS } from '../stores/profile'

const emit = defineEmits<{
  complete: []
  skip: []
}>()

const { setMyProfile } = useProfile()

const step = ref(1)
const selectedGender = ref<'male' | 'female' | 'other'>('male')
const selectedZodiac = ref('')

const canProceed = computed(() => {
  if (step.value === 1) return true
  if (step.value === 2) return !!selectedZodiac.value
  return true
})

function nextStep() {
  if (step.value < 3) {
    step.value++
  }
}

function prevStep() {
  if (step.value > 1) {
    step.value--
  }
}

function complete() {
  if (selectedZodiac.value) {
    setMyProfile(selectedGender.value, selectedZodiac.value)
  }
  emit('complete')
}

function skip() {
  emit('skip')
}
</script>

<template>
  <div class="setup-overlay">
    <div class="setup-modal">
      <button class="skip-btn" @click="skip">
        稍後設定
      </button>

      <!-- Step 1: 歡迎 -->
      <div v-if="step === 1" class="setup-step">
        <div class="step-icon">&#9733;</div>
        <h2>歡迎來到星語塔羅</h2>
        <p class="step-desc">
          設定你的星座資料，獲得個人化的運勢解讀與配對分析
        </p>
        <div class="step-features">
          <div class="feature">
            <sl-icon name="stars"></sl-icon>
            <span>專屬週運勢</span>
          </div>
          <div class="feature">
            <sl-icon name="heart"></sl-icon>
            <span>配對分析</span>
          </div>
          <div class="feature">
            <sl-icon name="moon-stars"></sl-icon>
            <span>天象解讀</span>
          </div>
        </div>
        <button class="btn-gold" @click="nextStep">
          開始設定
        </button>
      </div>

      <!-- Step 2: 選擇星座 -->
      <div v-else-if="step === 2" class="setup-step">
        <div class="step-indicator">
          <span class="dot active"></span>
          <span class="dot"></span>
        </div>
        <h2>你的星座是？</h2>
        <p class="step-desc">選擇你的太陽星座</p>

        <div class="zodiac-grid">
          <button
            v-for="sign in ZODIAC_SIGNS"
            :key="sign.code"
            :class="['zodiac-btn', { active: selectedZodiac === sign.code }]"
            @click="selectedZodiac = sign.code"
          >
            <span class="zodiac-symbol">{{ sign.symbol }}</span>
            <span class="zodiac-name">{{ sign.name }}</span>
          </button>
        </div>

        <div class="step-actions">
          <button class="btn-secondary" @click="prevStep">
            返回
          </button>
          <button
            class="btn-gold"
            @click="nextStep"
            :disabled="!selectedZodiac"
          >
            下一步
          </button>
        </div>
      </div>

      <!-- Step 3: 選擇性別 -->
      <div v-else-if="step === 3" class="setup-step">
        <div class="step-indicator">
          <span class="dot active"></span>
          <span class="dot active"></span>
        </div>
        <h2>你的性別是？</h2>
        <p class="step-desc">用於配對分析（可隨時修改）</p>

        <div class="gender-options">
          <label
            v-for="opt in GENDER_OPTIONS"
            :key="opt.value"
            :class="['gender-option', { active: selectedGender === opt.value }]"
          >
            <input
              type="radio"
              :value="opt.value"
              v-model="selectedGender"
              name="gender"
            />
            {{ opt.label }}
          </label>
        </div>

        <div class="step-actions">
          <button class="btn-secondary" @click="prevStep">
            返回
          </button>
          <button class="btn-gold" @click="complete">
            完成設定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.setup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(13, 11, 20, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-4);
}

.setup-modal {
  position: relative;
  width: 100%;
  max-width: 480px;
  background: var(--cosmos-dusk);
  border: 1px solid var(--border-gold);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.skip-btn {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  padding: var(--space-2) var(--space-3);
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 0.85rem;
  cursor: pointer;
}

.skip-btn:hover {
  color: var(--text-secondary);
}

.setup-step {
  text-align: center;
}

.step-icon {
  font-size: 3rem;
  color: var(--stellar-gold);
  margin-bottom: var(--space-4);
}

.step-indicator {
  display: flex;
  justify-content: center;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--border-default);
}

.dot.active {
  background: var(--stellar-gold);
}

.setup-step h2 {
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.step-desc {
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
}

.step-features {
  display: flex;
  justify-content: center;
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.feature {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-muted);
  font-size: 0.9rem;
}

.feature sl-icon {
  font-size: 1.5rem;
  color: var(--stellar-gold);
}

.zodiac-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-2);
  margin-bottom: var(--space-6);
}

.zodiac-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-3);
  background: var(--cosmos-night);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.zodiac-btn:hover {
  border-color: var(--border-gold);
}

.zodiac-btn.active {
  border-color: var(--stellar-gold);
  background: var(--astral-deep);
}

.zodiac-symbol {
  font-size: 1.5rem;
  margin-bottom: var(--space-1);
}

.zodiac-name {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.zodiac-btn.active .zodiac-name {
  color: var(--stellar-gold);
}

.gender-options {
  display: flex;
  justify-content: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.gender-option {
  padding: var(--space-3) var(--space-6);
  background: var(--cosmos-night);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.gender-option input {
  display: none;
}

.gender-option.active {
  border-color: var(--stellar-gold);
  background: var(--astral-deep);
  color: var(--stellar-gold);
}

.step-actions {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
}

.btn-secondary {
  padding: var(--space-3) var(--space-6);
  background: var(--cosmos-night);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
}

.btn-secondary:hover {
  border-color: var(--text-muted);
}

.btn-gold {
  padding: var(--space-3) var(--space-6);
}

.btn-gold:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .zodiac-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .step-features {
    flex-direction: column;
    gap: var(--space-3);
  }
}
</style>
