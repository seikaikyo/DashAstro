<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  title: string
  subtitle?: string
  badge?: string
  badgeClass?: string
  defaultOpen?: boolean
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  defaultOpen: false,
  badgeClass: ''
})

const isOpen = ref(props.defaultOpen)

const toggle = () => {
  isOpen.value = !isOpen.value
}

// 允許外部控制
const emit = defineEmits<{
  toggle: [isOpen: boolean]
}>()

watch(isOpen, (val) => {
  emit('toggle', val)
})
</script>

<template>
  <div :class="['collapsible-card', { open: isOpen }]">
    <button class="card-header" @click="toggle">
      <div class="header-left">
        <sl-icon v-if="icon" :name="icon" class="header-icon"></sl-icon>
        <div class="header-titles">
          <span class="header-title">{{ title }}</span>
          <span v-if="subtitle && !isOpen" class="header-subtitle">{{ subtitle }}</span>
        </div>
      </div>
      <div class="header-right">
        <span v-if="badge" :class="['header-badge', badgeClass]">{{ badge }}</span>
        <sl-icon :name="isOpen ? 'caret-up' : 'caret-down'" class="toggle-icon"></sl-icon>
      </div>
    </button>
    <div class="card-content" :class="{ expanded: isOpen }">
      <div class="content-inner">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.collapsible-card {
  background: var(--cosmos-dusk);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: border-color 0.2s;
}

.collapsible-card.open {
  border-color: var(--border-gold);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: var(--space-4);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  color: var(--text-primary);
  transition: background 0.2s;
}

.card-header:hover {
  background: rgba(255, 255, 255, 0.02);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.header-icon {
  font-size: 1.25rem;
  color: var(--stellar-gold);
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.header-title {
  font-weight: 500;
  font-size: 1rem;
}

.header-subtitle {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.header-badge {
  padding: var(--space-1) var(--space-2);
  background: var(--cosmos-night);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 500;
}

.header-badge.excellent {
  background: rgba(74, 155, 107, 0.2);
  color: #4A9B6B;
}

.header-badge.good {
  background: rgba(200, 160, 82, 0.2);
  color: var(--stellar-gold);
}

.header-badge.fair {
  background: rgba(139, 115, 85, 0.2);
  color: #C4A052;
}

.header-badge.caution {
  background: rgba(232, 141, 60, 0.2);
  color: #E88D3C;
}

.header-badge.warning {
  background: rgba(232, 93, 76, 0.2);
  color: #E85D4C;
}

.toggle-icon {
  color: var(--text-muted);
  transition: transform 0.2s;
}

.card-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}

.card-content.expanded {
  max-height: 2000px;
  transition: max-height 0.4s ease-in;
}

.content-inner {
  padding: 0 var(--space-4) var(--space-4);
  border-top: 1px solid var(--border-default);
}
</style>
