import { defineConfig } from 'astro/config'
import mdx from '@astrojs/mdx'
import sitemap from '@astrojs/sitemap'
import UnoCSS from 'unocss/astro'
import vue from '@astrojs/vue'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import partytown from '@astrojs/partytown'
import vercel from '@astrojs/vercel/serverless'

export default defineConfig({
  site: 'https://devanshshah.dev',
  output: 'static',
  adapter: vercel({
    webAnalytics: {
      enabled: true,
    },
  }),
  server: {
    port: 3000,
    host: true,
  },
  integrations: [
    mdx(),
    sitemap(),
    UnoCSS({
      injectReset: true,
    }),
    vue({
      jsx: true,
      include: ['**/*.vue'],
    }),
    partytown({
      config: {
        forward: ['dataLayer.push'],
        debug: false,
      },
    }),
  ],
  markdown: {
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatex],
    shikiConfig: {
      wrap: true,
    },
  },
})
