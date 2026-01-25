<script setup lang="ts">
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="footer">
    <div class="container footer-content">
      <p class="copyright">
        {{ currentYear }} DashAstro 星語塔羅
      </p>
      <p class="disclaimer">
        占卜結果僅供參考，請以理性態度看待
      </p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: var(--cosmos-night);
  border-top: 1px solid var(--border-default);
  padding: var(--space-6) 0;
  margin-top: auto;
}

.footer-content {
  text-align: center;
}

.copyright {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: var(--space-2);
}

.disclaimer {
  color: var(--text-muted);
  font-size: 0.75rem;
}
</style>
