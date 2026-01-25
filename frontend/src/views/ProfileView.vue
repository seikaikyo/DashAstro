<script setup lang="ts">
import { ref, watch } from 'vue'
import { useProfile, ZODIAC_SIGNS, GENDER_OPTIONS, getZodiacFromBirthDate } from '../stores/profile'
import type { Partner } from '../stores/profile'

const {
  profile,
  isProfileSet,
  myZodiac,
  myBirthDate,
  primaryPartner,
  getPartnerZodiac,
  setMyProfile,
  addPartner,
  removePartner,
  setPrimaryPartner
} = useProfile()

// 表單狀態
const selectedGender = ref(profile.value.gender || 'male')
const selectedZodiac = ref(profile.value.zodiacCode || '')
const selectedBirthDate = ref(profile.value.birthDate || '')

// 新增對象表單
const showAddPartner = ref(false)
const newPartner = ref({
  nickname: '',
  gender: 'female' as 'male' | 'female' | 'other',
  zodiacCode: '',
  birthDate: ''
})

// 根據生日自動選擇星座
watch(() => selectedBirthDate.value, (newDate) => {
  if (newDate) {
    const zodiac = getZodiacFromBirthDate(newDate)
    if (zodiac) {
      selectedZodiac.value = zodiac
    }
  }
})

watch(() => newPartner.value.birthDate, (newDate) => {
  if (newDate) {
    const zodiac = getZodiacFromBirthDate(newDate)
    if (zodiac) {
      newPartner.value.zodiacCode = zodiac
    }
  }
})

function saveMyProfile() {
  if (!selectedZodiac.value) return
  setMyProfile(
    selectedGender.value as 'male' | 'female' | 'other',
    selectedZodiac.value,
    selectedBirthDate.value || undefined
  )
}

function handleAddPartner() {
  if (!newPartner.value.zodiacCode) return

  try {
    addPartner({
      nickname: newPartner.value.nickname || getZodiacName(newPartner.value.zodiacCode),
      gender: newPartner.value.gender,
      zodiacCode: newPartner.value.zodiacCode,
      isPrimary: false,
      birthDate: newPartner.value.birthDate || undefined
    })

    // 重置表單
    newPartner.value = {
      nickname: '',
      gender: 'female',
      zodiacCode: '',
      birthDate: ''
    }
    showAddPartner.value = false
  } catch (e: any) {
    alert(e.message)
  }
}

function getZodiacName(code: string) {
  return ZODIAC_SIGNS.find(z => z.code === code)?.name || code
}

function getZodiacSymbol(code: string) {
  return ZODIAC_SIGNS.find(z => z.code === code)?.symbol || ''
}

function getGenderLabel(gender: string) {
  return GENDER_OPTIONS.find(g => g.value === gender)?.label || gender
}
</script>

<template>
  <div class="profile-page">
    <div class="container">
      <header class="page-header">
        <router-link to="/" class="back-link">
          <sl-icon name="arrow-left"></sl-icon>
        </router-link>
        <h1>我的收藏</h1>
      </header>

      <!-- 我的資料 -->
      <section class="profile-section card">
        <h2>我的資料</h2>

        <div class="form-group">
          <label>生日</label>
          <sl-input
            type="date"
            v-model="selectedBirthDate"
            :max="new Date().toISOString().split('T')[0]"
            help-text="填寫生日可使用宿曜道運勢預測"
          ></sl-input>
        </div>

        <div class="form-group">
          <label>性別</label>
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
        </div>

        <div class="form-group">
          <label>
            我的星座
            <span v-if="selectedBirthDate" class="auto-detect-hint">（已根據生日自動選擇）</span>
          </label>
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
        </div>

        <button
          class="btn-gold save-btn"
          @click="saveMyProfile"
          :disabled="!selectedZodiac"
        >
          儲存我的資料
        </button>

        <div v-if="isProfileSet" class="profile-summary">
          <sl-icon name="check-circle"></sl-icon>
          已設定：{{ getGenderLabel(profile.gender!) }} {{ myZodiac?.name }}
          <span v-if="myBirthDate">（{{ myBirthDate }}）</span>
        </div>
      </section>

      <!-- 關注對象 -->
      <section class="partners-section card">
        <div class="section-header">
          <h2>關注對象</h2>
          <span class="partner-count">{{ profile.partners.length }}/5</span>
        </div>

        <p class="section-desc">
          新增關注對象，在週運勢和塔羅占卜時自動帶入配對分析
        </p>

        <!-- 對象列表 -->
        <div v-if="profile.partners.length > 0" class="partner-list">
          <div
            v-for="partner in profile.partners"
            :key="partner.id"
            :class="['partner-card', { primary: partner.isPrimary }]"
          >
            <div class="partner-info">
              <span class="partner-symbol">{{ getZodiacSymbol(partner.zodiacCode) }}</span>
              <div class="partner-details">
                <span class="partner-name">{{ partner.nickname }}</span>
                <span class="partner-meta">
                  {{ getGenderLabel(partner.gender) }} {{ getZodiacName(partner.zodiacCode) }}
                  <span v-if="partner.birthDate" class="partner-birth">{{ partner.birthDate }}</span>
                </span>
              </div>
            </div>
            <div class="partner-actions">
              <button
                v-if="!partner.isPrimary"
                class="action-btn"
                @click="setPrimaryPartner(partner.id)"
                title="設為主要"
              >
                <sl-icon name="star"></sl-icon>
              </button>
              <sl-icon v-else name="star-fill" class="primary-star"></sl-icon>
              <button
                class="action-btn delete"
                @click="removePartner(partner.id)"
                title="移除"
              >
                <sl-icon name="trash"></sl-icon>
              </button>
            </div>
          </div>
        </div>

        <p v-else class="no-partners">
          尚未新增關注對象
        </p>

        <!-- 新增對象 -->
        <div v-if="showAddPartner" class="add-partner-form">
          <div class="form-row">
            <sl-input
              v-model="newPartner.nickname"
              placeholder="暱稱（選填）"
              size="small"
            ></sl-input>
            <sl-select
              v-model="newPartner.gender"
              size="small"
            >
              <sl-option
                v-for="opt in GENDER_OPTIONS"
                :key="opt.value"
                :value="opt.value"
              >
                {{ opt.label }}
              </sl-option>
            </sl-select>
          </div>

          <div class="form-row">
            <sl-input
              type="date"
              v-model="newPartner.birthDate"
              :max="new Date().toISOString().split('T')[0]"
              size="small"
              label="生日（選填，可用於宿曜道）"
            ></sl-input>
          </div>

          <div class="form-group">
            <label>
              星座
              <span v-if="newPartner.birthDate" class="auto-detect-hint">（已根據生日自動選擇）</span>
            </label>
            <div class="zodiac-grid small">
              <button
                v-for="sign in ZODIAC_SIGNS"
                :key="sign.code"
                :class="['zodiac-btn', { active: newPartner.zodiacCode === sign.code }]"
                @click="newPartner.zodiacCode = sign.code"
              >
                <span class="zodiac-symbol">{{ sign.symbol }}</span>
                <span class="zodiac-name">{{ sign.name }}</span>
              </button>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn-secondary" @click="showAddPartner = false">
              取消
            </button>
            <button
              class="btn-gold"
              @click="handleAddPartner"
              :disabled="!newPartner.zodiacCode"
            >
              確認新增
            </button>
          </div>
        </div>

        <button
          v-else-if="profile.partners.length < 5"
          class="add-partner-btn"
          @click="showAddPartner = true"
        >
          <sl-icon name="plus-circle"></sl-icon>
          新增關注對象
        </button>
      </section>

      <!-- 使用說明 -->
      <section class="tips-section card">
        <h3>如何使用配對分析</h3>
        <ul>
          <li>設定主要關注對象後，週運勢的感情區塊會自動顯示配對分析</li>
          <li>塔羅占卜選擇感情相關牌陣時，AI 解讀會加入雙方星座分析</li>
          <li>所有資料僅儲存在你的裝置上，不會上傳到伺服器</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  padding-bottom: var(--space-12);
}

.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.back-link {
  color: var(--text-secondary);
  font-size: 1.25rem;
}

.back-link:hover {
  color: var(--stellar-gold);
}

.page-header h1 {
  margin: 0;
}

.profile-section,
.partners-section,
.tips-section {
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}

.profile-section h2,
.partners-section h2 {
  margin-bottom: var(--space-4);
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.gender-options {
  display: flex;
  gap: var(--space-3);
}

.gender-option {
  padding: var(--space-2) var(--space-4);
  background: var(--cosmos-dusk);
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

.zodiac-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-2);
}

.zodiac-grid.small {
  grid-template-columns: repeat(6, 1fr);
}

.zodiac-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-3);
  background: var(--cosmos-dusk);
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

.zodiac-grid.small .zodiac-symbol {
  font-size: 1.2rem;
}

.zodiac-name {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.zodiac-btn.active .zodiac-name {
  color: var(--stellar-gold);
}

.save-btn {
  width: 100%;
  padding: var(--space-3);
}

.profile-summary {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-4);
  padding: var(--space-3);
  background: rgba(74, 155, 107, 0.1);
  border-radius: var(--radius-md);
  color: var(--success);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.partner-count {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.section-desc {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: var(--space-4);
}

.partner-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.partner-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--cosmos-dusk);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
}

.partner-card.primary {
  border-color: var(--border-gold);
}

.partner-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.partner-symbol {
  font-size: 1.5rem;
}

.partner-details {
  display: flex;
  flex-direction: column;
}

.partner-name {
  font-weight: 500;
}

.partner-meta {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.partner-birth {
  margin-left: var(--space-2);
  color: var(--stellar-gold);
}

.auto-detect-hint {
  font-size: 0.8rem;
  color: var(--stellar-gold);
  font-weight: normal;
}

.partner-actions {
  display: flex;
  gap: var(--space-2);
}

.action-btn {
  padding: var(--space-2);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.2s;
}

.action-btn:hover {
  color: var(--stellar-gold);
}

.action-btn.delete:hover {
  color: var(--error);
}

.primary-star {
  color: var(--stellar-gold);
  padding: var(--space-2);
}

.no-partners {
  color: var(--text-muted);
  text-align: center;
  padding: var(--space-4);
}

.add-partner-form {
  padding: var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.form-row {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.form-row sl-input {
  flex: 1;
}

.form-row sl-select {
  width: 100px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.btn-secondary {
  padding: var(--space-2) var(--space-4);
  background: var(--cosmos-dusk);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
}

.btn-secondary:hover {
  border-color: var(--text-muted);
}

.add-partner-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-3);
  background: none;
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.add-partner-btn:hover {
  border-color: var(--stellar-gold);
  color: var(--stellar-gold);
}

.tips-section {
  padding: var(--space-4);
}

.tips-section h3 {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-3);
}

.tips-section ul {
  margin: 0;
  padding-left: var(--space-5);
}

.tips-section li {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}

@media (max-width: 480px) {
  .zodiac-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .zodiac-grid.small {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
