# Role: Senior Frontend Developer & Nuxt 4 & Vue 3 Expert

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