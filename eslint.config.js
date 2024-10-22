import antfu from '@antfu/eslint-config'

export default antfu({
  vue: true,
  typescript: true,
  astro: true,
  formatters: {
    astro: true,
    css: true,
  },
  rules: {
    'no-irregular-whitespace': 'off', // Disable the rule to allow irregular whitespace
  },
})
