import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/',
  build: {
    emptyOutDir: true,
    outDir: '../public',
  },
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['apple-touch-icon.svg', 'icon-192x192.svg', 'icon-512x512.svg', 'mask-icon.svg', 'vite.svg'],
      manifest: {
        name: '灵值生态园 - 智能体APP',
        short_name: '灵值生态园',
        description: '灵值生态园智能体应用 - 用户旅程管理、经济模型计算、智能对话',
        theme_color: '#4F46E5',
        background_color: '#FFFFFF',
        display: 'standalone',
        orientation: 'portrait-primary',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/icon-192x192.svg',
            sizes: '192x192',
            type: 'image/svg+xml',
            purpose: 'any maskable'
          },
          {
            src: '/icon-512x512.svg',
            sizes: '512x512',
            type: 'image/svg+xml',
            purpose: 'any maskable'
          }
        ],
        categories: [
          'productivity',
          'finance',
          'education',
          'lifestyle'
        ],
        shortcuts: [
          {
            name: '智能对话',
            short_name: '对话',
            description: '快速进入智能对话',
            url: '/chat',
            icons: [{ src: '/icon-192x192.png', sizes: '192x192' }]
          },
          {
            name: '经济模型',
            short_name: '经济',
            description: '查看经济模型计算',
            url: '/economy',
            icons: [{ src: '/icon-192x192.png', sizes: '192x192' }]
          },
          {
            name: '个人中心',
            short_name: '我的',
            description: '查看个人信息',
            url: '/profile',
            icons: [{ src: '/icon-192x192.png', sizes: '192x192' }]
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2,ttf,eot}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\./i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 24 * 60 * 60 // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
  ],
  server: {
    port: 3000,
    open: true
  }
})
