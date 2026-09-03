// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'
import ts from 'typescript-eslint'
import pluginVue from 'eslint-plugin-vue'
import pluginPrettier from 'eslint-plugin-prettier'
import configPrettier from 'eslint-config-prettier'
import tsParser from '@typescript-eslint/parser'
import vueParser from 'vue-eslint-parser'

export default withNuxt(
  {
    ignores: [
      'node_modules/**',
      '.nuxt/**',
      '.output/**',
      '.data/**',
      '.nitro/**',
      '.cache/**',
      'dist/**',
      'coverage/**',
      'public/**',
      'pnpm-lock.yaml',
    ],
  },
  ...ts.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  configPrettier,
  {
    name: 'learnify/nuxt4-vue-ts-parser',
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tsParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
  },
  {
    name: 'learnify/nuxt4-custom-rules',
    plugins: {
      prettier: pluginPrettier,
    },
    rules: {
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'no-debugger': 'error',
      'prefer-const': 'error',
      'no-var': 'error',
      eqeqeq: ['error', 'always'],
      curly: ['error', 'all'],

      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-non-null-assertion': 'warn',
      '@typescript-eslint/consistent-type-imports': 'off',

      'vue/multi-word-component-names': 'off',
      'vue/component-api-style': ['error', ['script-setup']],
      'vue/block-lang': ['error', { script: { lang: 'ts' }, style: { lang: 'css' } }],
      'vue/block-order': ['error', { order: ['script', 'template', 'style'] }],
      'vue/html-self-closing': [
        'error',
        {
          html: { void: 'always', normal: 'always', component: 'always' },
          svg: 'always',
          math: 'always',
        },
      ],
      'vue/define-macros-order': [
        'error',
        { order: ['defineOptions', 'defineProps', 'defineEmits', 'defineSlots'] },
      ],
      'vue/padding-line-between-tags': ['error', [{ blankLine: 'always', prev: '*', next: '*' }]],

      'prettier/prettier': 'warn',
    },
  },
)
