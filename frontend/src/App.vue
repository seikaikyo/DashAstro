<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import ProfileSetup from './components/ProfileSetup.vue'
import { useProfile } from './stores/profile'

const { isProfileSet } = useProfile()
const showSetup = ref(false)
const setupDismissed = ref(false)

const SETUP_DISMISSED_KEY = 'dashastro_setup_dismissed'

onMounted(() => {
  // 檢查是否已略過設定
  const dismissed = localStorage.getItem(SETUP_DISMISSED_KEY)
  if (dismissed) {
    setupDismissed.value = true
  }

  // 未設定且未略過時顯示引導
  if (!isProfileSet.value && !setupDismissed.value) {
    showSetup.value = true
  }
})

function handleSetupComplete() {
  showSetup.value = false
}

function handleSetupSkip() {
  showSetup.value = false
  setupDismissed.value = true
  localStorage.setItem(SETUP_DISMISSED_KEY, 'true')
}
</script>

<template>
  <div class="app">
    <div class="stardust"></div>
    <AppHeader />
    <main class="main-content">
      <RouterView />
    </main>
    <AppFooter />

    <!-- 首次造訪引導 -->
    <ProfileSetup
      v-if="showSetup"
      @complete="handleSetupComplete"
      @skip="handleSetupSkip"
    />
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: var(--space-8) 0;
}
</style>
