---
alwaysApply: true
description: "Workflow routing map — always injected first. Directs the agent to the correct domain rule for the task at hand."
---

# This is NOT an executable domain rule — it is the INDEX into the 6 executable rules below.
# Skill analogue: `.trae/skill/orchestration.md`. When the agent reads this file, the intent is to
# pick the correct sub-rule (plan, backend, frontend, infra, reviewer, tester) for the task at hand.
# Do NOT add domain implementation guidelines or workflow-step enforcement to this file.

# Agent Workflow Map

- For planning architecture or features -> refer to `.trae/rules/plan.md`
- For API/DB implementation -> refer to `.trae/rules/backend.md`
- For UI/Component implementation -> refer to `.trae/rules/frontend.md`
- For Docker, Nginx, Postgres/Redis/Mailpit, Makefiles, env config -> refer to `.trae/rules/infra.md`
- For code reviews & quality checks -> refer to `.trae/rules/reviewer.md`
- For unit & integration tests -> refer to `.trae/rules/tester.md`