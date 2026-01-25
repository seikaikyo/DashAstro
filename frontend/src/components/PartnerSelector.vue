<script setup lang="ts">
import { computed } from 'vue'
import { useProfile, type Partner } from '../stores/profile'

const props = defineProps<{
  modelValue: Partner | null
}>()

const emit = defineEmits<{
  'update:modelValue': [partner: Partner | null]
}>()

const { profile, getPartnerZodiac } = useProfile()

const partners = computed(() => profile.value.partners)

function selectPartner(partner: Partner) {
  emit('update:modelValue', partner)
}

function getDisplayName(partner: Partner): string {
  const zodiac = getPartnerZodiac(partner)
  return partner.nickname || zodiac?.name || '對象'
}
</script>

<template>
  <div v-if="partners.length > 1" class="partner-selector">
    <button
      v-for="partner in partners"
      :key="partner.id"
      :class="['partner-btn', { active: modelValue?.id === partner.id }]"
      @click="selectPartner(partner)"
    >
      <span class="partner-symbol">{{ getPartnerZodiac(partner)?.symbol }}</span>
      <span class="partner-name">{{ getDisplayName(partner) }}</span>
    </button>
  </div>
</template>

<style scoped>
.partner-selector {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-bottom: var(--space-4);
}

.partner-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--cosmos-night);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.partner-btn:hover {
  border-color: var(--astral-medium);
}

.partner-btn.active {
  border-color: var(--stellar-gold);
  background: var(--astral-deep);
  color: var(--stellar-gold);
}

.partner-symbol {
  font-size: 1.1rem;
}

.partner-name {
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
