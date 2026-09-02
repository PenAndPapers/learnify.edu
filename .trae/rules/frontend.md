---
alwaysApply: false
description: Use when building client-side code, Nuxt 4 pages, Vue 3 components, composables, Pinia stores, or applying Tailwind CSS styling.
globs:
  - "frontend/nuxt4/**/*.vue"
  - "frontend/nuxt4/**/*.ts"
  - "frontend/nuxt4/**/*.tsx"
  - "frontend/nuxt4/**/*.js"
  - "frontend/nuxt4/nuxt.config.ts"
  - "frontend/nuxt4/package.json"
---

# Frontend Development Rules & Standards

## 1. Core Stack Standards
- **Framework:** Vue 3 (Composition API exclusively) & Nuxt 4 (`app/` directory architecture)
- **Language:** TypeScript in strict mode. Never use `any` or loose types.
- **Styling:** Tailwind CSS (utility-first approach). **Deferred pending project setup** — do not generate Tailwind utilities or `@apply` rules until `tailwindcss`, `@nuxtjs/tailwindcss` (or equivalent) are listed in `package.json` and modules in `nuxt.config.ts`.
- **State Management:** Pinia (Setup Store syntax) or Nuxt `useState` composables. **Pinia deferred pending project setup** — do not generate `defineStore(...)` usage until `pinia`, `@pinia/nuxt` (or equivalent) are listed in `package.json` / `nuxt.config.ts` modules. In the interim, prefer `useState` for small, global pieces of reactive state.
- **Build / Package Manager:** `pnpm`. Installs must use `pnpm install --frozen-lockfile` in CI/container-builds.
- **Quality Commands (host-native inside frontend/nuxt4):**
  - `pnpm dev` — dev server
  - `pnpm build` / `pnpm generate` / `pnpm preview` — build targets
  - `pnpm typecheck` (or `npx nuxi typecheck`) — TypeScript strict verification
  - Existing `frontend-nuxt-*` Make targets in the root Makefile mirror these scripts.

---

## 2. Vue & Nuxt Architecture

### Component Standards
- Always use `<script setup lang="ts">`. Options API is strictly prohibited.
- Place all client code under `frontend/nuxt4/app/` (`components/`, `pages/`, `composables/`, `layouts/`, `stores/`). Do not create a legacy `pages/` folder at the package root — Nuxt 4 routes live under `app/`.
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
  ```

### API Integration
- Use `$fetch` or a dedicated custom `$ofetch` wrapper module that maps 1:1 to backend FastAPI endpoints.
- **204 Handling:** On DELETE / void endpoints, expect empty response bodies. Never call `.json()` or parse a 204 response body.
- **Error Envelopes:** All non-2xx responses from the backend use `{ error: "CODE", detail: "msg" }`. The detail key is **singular** — never check for plural `"details"`.
- **API Base URL:** Never hardcode `http://localhost:8000` in components. Read the backend origin from runtime config (`useRuntimeConfig()`) or environment variables. Dev-time proxy via Nginx is preferred — the same `/api` prefix should work in dev and prod.

### Type Safety & Forms
- Define TypeScript interfaces that **exactly mirror** Pydantic response/request models emitted by the FastAPI backend. If the backend adds/renames a field, the frontend interface changes in lockstep.
- Forms sending `PATCH` requests must transmit only the fields actually modified by the user (matches backend `model_dump(exclude_unset=True)` partial update semantics). Never re-POST the entire record with stale values for untouched keys.

### Auth & Tokens
- Store JWT access/refresh tokens using Nuxt composables — `useCookie` (if you accept the tradeoff of CSRF mitigation via SameSite settings) or in-memory for higher-security SPA flows.
- Add a fetch/ofetch interceptor that auto-refreshes the access token and retries the original 401'd request exactly once, then surfaces the error on the second failure.