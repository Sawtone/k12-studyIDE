import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 允许访问的域名
const allowedOrigins = [
  'https://k12ide.sawtone.site',
  'https://k12-study-ide.vercel.app'
]

export default defineConfig({
  plugins: [react()],
  server: {
    cors: {
      origin: allowedOrigins,
      credentials: true,
    },
    proxy: {
      '/api': {
        target: 'https://lovely-motivation-production.up.railway.app',
        changeOrigin: true,
        secure: true,
      },
    },
  },
  preview: {
    cors: {
      origin: allowedOrigins,
      credentials: true,
    },
  },
})
