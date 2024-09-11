/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        'custom-blue': '#144EE3',
        'custom-pink': '#EB568E',
      },
      backgroundImage: {
        'custom-gradient': 'linear-gradient(90deg, #144EE3 0%, #EB568E 100%)',
      },
    },
  },
  plugins: [],
};