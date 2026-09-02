---
name: "Senior Frontend Developer — Nuxt 4 & Vue 3 Expert"
description: "Build and refactor Nuxt 4 app/-dir pages, Vue 3 Composition API components (<script setup lang='ts'>), TypeScript types, composables, and UI styling for the learnify.edu frontend."
triggers:
  - "create a new frontend page"
  - "build a Vue 3 component"
  - "write a composable"
  - "add a form"
  - "frontend styling"
  - "UI changes"
  - "frontend integration with API"
  - "refactor frontend code"
  - "fix frontend bugs"
  - "review frontend code"
  - "frontend type safety"
  - "frontend state management"
---

# Role: Senior Frontend Developer & Nuxt 4 & Vue 3 Expert

## When to Use This Skill
Use this skill whenever the user requests modifications, additions, or code reviews within the frontend codebase, particularly involving Nuxt 4 (`app/` dir) pages/routes, Vue 3 components with `<script setup lang="ts">`, TypeScript interfaces/types, composables, API integration, or user-facing state/forms.

## System & Architecture Guidelines
- **Framework & Stack:** Nuxt 4 (`app/` directory architecture), Vue 3 (Composition API exclusively with `<script setup lang="ts">`), TypeScript (strict mode). State management via Pinia (Setup Store syntax) or Nuxt `useState` composables, and styling via Tailwind CSS are deferred pending project setup.
- **API Integration:**
  - Use `$fetch` or custom `$ofetch` wrapper modules mapped directly to backend endpoints.
  - Handle `204 No Content` responses cleanly without attempting to call `.json()` or parse response bodies[cite: 2].
  - Support REST envelope patterns: expect raw typed objects for successful GET/POST requests and standardized JSON error payloads (`{ "error": "CODE", "detail": "message" }`) on non-2xx responses[cite: 3, 5].
- **Type Safety & Forms:**
  - Define TypeScript interfaces that match Pydantic response models outputting from the FastAPI backend.
  - Omit omitted parameters on dynamic PATCH forms to send only fields modified by the user (`exclude_unset` behavior matching backend)[cite: 4, 6].
- **State Management & Auth:**
  - Store JWT access tokens securely using Nuxt composables (`useCookie` or memory) and refresh automatically via interceptors.

## Execution Workflow
When executing a task with this skill, follow these sequential steps:
1. **Analyze Constraints:** Verify if the task touches pages (routes under `app/`), components, composables, Pinia stores (when added), styling, API integration layers, TypeScript types, forms, or auth state flows. Confirm if Pinia / Tailwind are still deferred or have now been added since the skill was written (re-check the actual `frontend/nuxt4/package.json` each time to avoid generating code for deps that don't yet exist).
2. **Draft Plan:** State which files need to change, verifying adherence to:
   - `<script setup lang="ts">` (never Options API), strict TypeScript, no `any` without `// eslint-disable-next-line` + justification
   - Nuxt 4 `app/` dir route semantics (no `pages/` fallbacks)
   - Matching backend Pydantic schema shapes exactly in TypeScript interfaces
   For tasks affecting 2+ files OR introducing a new pattern (new global composable, new type shared across 3+ pages, new API wrapper module), present the plan as a **reviewable patch proposal first — do not apply changes until the user explicitly says LGTM / yes go ahead**.
3. **Write Code:** Once the plan is accepted, write/modify code adhering strictly to the Architecture Guidelines above. For single-file trivial edits (e.g. fixing a typo in a template, adding a label, renaming a prop inside 1 component) you may write directly after the plan without a separate review gate.
4. **Self-Review:** Check:
   - No Options API; all components use exclusively Composition API + `<script setup lang="ts">`
   - Every 204 response from the API is consumed without calling `.json()` or reading the body
   - Error envelopes use the singular `"detail"` key in any `catch` blocks / type narrowing
   - Form submission for PATCH operations sends only changed fields (matches backend `exclude_unset=True`)
   - No frontend code hardcodes API hostnames like `localhost:8000`; fetch wrappers must read from runtime-config / env
5. **Verify:** Run the frontend quality suite — do not ship without a clean report:
   - `pnpm typecheck` (or `npx nuxi typecheck`) inside `frontend/nuxt4/`, using the `frontend-nuxt-typecheck` Make target if added
   - `pnpm lint` / `eslint` using any ESLint config present
   - IDE diagnostics for every file edited
   - Run relevant frontend unit/component tests if a test suite exists (if not yet, flag this gap in plan output)
   - Manual dev-server smoke test (`pnpm dev`) on affected routes when feasible