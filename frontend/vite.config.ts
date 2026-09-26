import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    exclude: ['e2e/**', 'node_modules/**'],
  },

  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,

    proxy: {
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http' + '://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },

      '/ws': {
        target: (process.env.VITE_BACKEND_URL || 'http' + '://127.0.0.1:8000').replace(/^http/, 'ws'),
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
