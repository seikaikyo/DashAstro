<script setup lang="ts">
// 骨架載入元件 - 改善首屏感知效能
</script>

<template>
  <div class="skeleton-container">
    <!-- Header skeleton -->
    <header class="skeleton-header">
      <div class="skeleton-logo"></div>
      <nav class="skeleton-nav">
        <div class="skeleton-nav-item"></div>
        <div class="skeleton-nav-item"></div>
        <div class="skeleton-nav-item"></div>
        <div class="skeleton-nav-item"></div>
      </nav>
    </header>

    <!-- Hero skeleton -->
    <section class="skeleton-hero">
      <div class="skeleton-title"></div>
      <div class="skeleton-subtitle"></div>
      <div class="skeleton-badge"></div>
      <div class="skeleton-actions">
        <div class="skeleton-button"></div>
        <div class="skeleton-button skeleton-button-outline"></div>
      </div>
    </section>

    <!-- Feature cards skeleton -->
    <section class="skeleton-features">
      <div class="skeleton-card"></div>
      <div class="skeleton-card"></div>
      <div class="skeleton-card"></div>
      <div class="skeleton-card"></div>
    </section>
  </div>
</template>

<style scoped>
.skeleton-container {
  min-height: 100vh;
  background: var(--cosmos-void, #0a0a0f);
}

/* 骨架動畫 */
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.skeleton-header,
.skeleton-logo,
.skeleton-nav-item,
.skeleton-title,
.skeleton-subtitle,
.skeleton-badge,
.skeleton-button,
.skeleton-card {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.03) 25%,
    rgba(255, 255, 255, 0.08) 50%,
    rgba(255, 255, 255, 0.03) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

/* Header */
.skeleton-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(10, 10, 15, 0.95);
}

.skeleton-logo {
  width: 120px;
  height: 32px;
}

.skeleton-nav {
  display: flex;
  gap: 1.5rem;
}

.skeleton-nav-item {
  width: 60px;
  height: 20px;
}

/* Hero */
.skeleton-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 2rem;
  text-align: center;
}

.skeleton-title {
  width: 280px;
  height: 56px;
  margin-bottom: 1rem;
}

.skeleton-subtitle {
  width: 320px;
  height: 24px;
  margin-bottom: 1.5rem;
}

.skeleton-badge {
  width: 200px;
  height: 36px;
  border-radius: 999px;
  margin-bottom: 2rem;
}

.skeleton-actions {
  display: flex;
  gap: 1rem;
}

.skeleton-button {
  width: 140px;
  height: 44px;
}

.skeleton-button-outline {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Feature cards */
.skeleton-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 3rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.skeleton-card {
  height: 200px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 響應式 */
@media (max-width: 768px) {
  .skeleton-nav {
    display: none;
  }

  .skeleton-title {
    width: 200px;
    height: 40px;
  }

  .skeleton-subtitle {
    width: 240px;
    height: 20px;
  }

  .skeleton-actions {
    flex-direction: column;
  }

  .skeleton-features {
    grid-template-columns: 1fr;
    padding: 2rem 1rem;
  }
}
</style>
