import legacy from '@vitejs/plugin-legacy'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'GRMMA le BuNaMo 7 Gramadán',
        short_name: 'FlashPWA',
        description: 'Irish language learning flashcard app for grammar practice',
        theme_color: '#3880ff',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/flashpwa/',
        scope: '/flashpwa/',
        icons: [
          {
            src: "/flashpwa/icon.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any maskable"
          },
          {
            src: "/flashpwa/favicon.png", 
            sizes: "192x192",
            type: "image/png"
          }
        ],
        screenshots: [
          {
            src: "/flashpwa/screenshot.png",
            form_factor: "narrow",
            sizes: "364x765",
            "type": "image/png",
            label: "verb card"
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,json}']
      }
    }),
    legacy()
  ],
  base: "/flashpwa/",
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom'
  }
})
