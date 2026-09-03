import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

const appDir = new URL('./app', import.meta.url).pathname

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', '.nuxt', '.output', '.data'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', '.nuxt/', '.output/', 'dist/'],
    },
  },
  resolve: {
    alias: {
      '~': appDir,
      '@': appDir,
    },
  },
})
