<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const menuOpen = ref(false)

const navItems = [
  { path: '/', label: '首頁', icon: 'house' },
  { path: '/horoscope', label: '星座運勢', icon: 'stars' },
  { path: '/tarot', label: '塔羅占卜', icon: 'layers' },
  { path: '/sky', label: '今日天象', icon: 'moon-stars' }
]

const isActive = (path: string) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <header class="header">
    <div class="container header-content">
      <router-link to="/" class="logo">
        <span class="logo-icon">&#9733;</span>
        <span class="logo-text">星語塔羅</span>
      </router-link>

      <nav class="nav-desktop">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="['nav-link', { active: isActive(item.path) }]"
        >
          <sl-icon :name="item.icon"></sl-icon>
          {{ item.label }}
        </router-link>
      </nav>

      <sl-icon-button
        name="list"
        class="menu-toggle"
        @click="menuOpen = !menuOpen"
      ></sl-icon-button>
    </div>

    <nav :class="['nav-mobile', { open: menuOpen }]">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :class="['nav-link', { active: isActive(item.path) }]"
        @click="menuOpen = false"
      >
        <sl-icon :name="item.icon"></sl-icon>
        {{ item.label }}
      </router-link>
    </nav>
  </header>
</template>

<style scoped>
.header {
  background: var(--cosmos-night);
  border-bottom: 1px solid var(--border-default);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-display);
  font-size: 1.25rem;
  color: var(--text-primary);
}

.logo-icon {
  color: var(--stellar-gold);
  font-size: 1.5rem;
}

.nav-desktop {
  display: flex;
  gap: var(--space-6);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-secondary);
  font-size: 0.95rem;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--cosmos-dusk);
}

.nav-link.active {
  color: var(--stellar-gold);
}

.menu-toggle {
  display: none;
  font-size: 1.5rem;
  color: var(--text-primary);
}

.nav-mobile {
  display: none;
  flex-direction: column;
  padding: var(--space-4);
  border-top: 1px solid var(--border-default);
}

@media (max-width: 768px) {
  .nav-desktop {
    display: none;
  }

  .menu-toggle {
    display: block;
  }

  .nav-mobile {
    display: none;
  }

  .nav-mobile.open {
    display: flex;
  }

  .nav-mobile .nav-link {
    padding: var(--space-3) var(--space-4);
  }
}
</style>
