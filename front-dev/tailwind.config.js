const colors = require('tailwindcss/colors')

module.exports = {
  purge: [
    '../templates/*.html',
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      ...colors,
    },
    extend: {
      typography: {
        DEFAULT: {
          css: {
            p: {
              marginTop: '0.75em',
              marginBottom: '0.75em',
            },
            pre: {
              marginTop: '1em',
              marginBottom: '1em',
              lineHeight: 1.5,
              fontSize: '0.75em',
            },
            img: {
              marginTop: '1em',
              marginBottom: '1em',
            },
            h2: {
              fontWeight: 'inherit'
            },
          }
        }
      }
    },
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/typography'),
  ],
}
