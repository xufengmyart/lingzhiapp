import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/',
  build: {
    emptyOutDir: true,
    outDir: '../public',
  },
  plugins: [
    react()
  ],
  server: {
    port: 3000,
    open: true
  }
})
