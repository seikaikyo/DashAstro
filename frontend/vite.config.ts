import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // 讓 Vue 忽略 Shoelace 的 sl- 開頭元件
          isCustomElement: (tag) => tag.startsWith('sl-')
        }
      }
    })
  ],
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  server: {
    port: 5173
  }
})
