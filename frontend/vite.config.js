import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // String shorthand: any request to /api/...
      // will be proxied to your backend
      '/api': {
        target: 'http://127.0.0.1:8003',
        changeOrigin: true, // a good practice for vhosts
        secure: false,      // if your backend is HTTP, not HTTPS
      }
    }
  }
})
