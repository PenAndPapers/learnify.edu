---
alwaysApply: false
description: Use when building client-side code, Nuxt 4 pages, Vue 3 components, composables, Pinia stores, or applying Tailwind CSS styling.
---

# Frontend Development Rules & Standards

## 1. Core Stack Standards
- **Framework:** Vue 3 (Composition API exclusively) & Nuxt 4 (`app/` directory architecture)
- **Language:** TypeScript in strict mode. Never use `any` or loose types.
- **Styling:** Tailwind CSS (utility-first approach)
- **State Management:** Pinia (Setup Store syntax) or Nuxt `useState` composables

---

## 2. Vue & Nuxt Architecture

### Component Standards
- Always use `<script setup lang="ts">`. Options API is strictly prohibited.
- Place all client code under `frontend/nuxt4/app/` (`components/`, `pages/`, `composables/`, `layouts/`, `stores/`).
- Use **Component-Driven Design**: Keep components small, modular, and single-responsibility.
  - **Base / UI Components:** Pure presentation components (buttons, inputs, modals) with no direct business logic.
  - **Feature Components:** Domain-specific components handling user interaction and state.

### Props, Emits & Reactivity
- Use macro type definitions for props and emits:
  ```typescript
  const props = defineProps<{
    title: string
    isActive?: boolean
  }>()

  const emit = defineEmits<{
    (e: 'update:isActive', value: boolean): void
  }>()