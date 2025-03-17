import { defineConfig } from 'vitepress'
import svgLoader from 'vite-svg-loader'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "OpsLoom Docs",
  description: "Guide for OpsLoom",
  head: [
    // ['script', { type: 'module', crossorigin: 'true', src: '/example.js' }],
    // ['link', { rel: 'stylesheet', crossorigin: 'true', href: '/example.css' }]
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ],
  vite: {
    assetsInclude: ['**/*.svg'],
    plugins: [svgLoader()]
    // resolve: {
    //   alias: {
    //     '@': '../assets'
    //   }
    // }
  },
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Docs', link: '/introduction' }
    ],
    logo: {dark: '/logo/dark.svg', light: "/logo/light.svg"},
    siteTitle: false,

    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Introduction', link: '/introduction' },
          { text: 'Core Concepts & Architecture', link: '/architecture' },
          { text: 'Setting Up Locally', link: '/setting-up-locally' },
        ]
      },
      {
        text: 'User Guide',
        items: [
          { text: 'Creating Your First Assistant', link: '/creating-your-first-assistant' },
          { text: 'Styling', link: '/styling' },
          { text: 'Embedding', link: '/embedding' }
        ]
      },
      {
        text: 'Examples',
        items: [
          { text: 'RAG AI Assistant', link: '/rag-assistant' },
          { text: 'Text to SQL (AWS Cost Calculator)', link: '/text-to-sql-assistant' }
        ]
      },
      {
        text: 'References',
        items: [
          { text: 'FAQs', link: '/faqs' },
        ]
      }
    ],
    footer: {
      // message: 'Released under the <a href="https://github.com/vuejs/vitepress/blob/main/LICENSE">MIT License</a>.',
      copyright: '©2025 Opsloom'
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/leaninnovationlabs/opsloom' }
    ]
  }
})
