# This is NOT an executable skill persona — it is the INDEX into the 6 executable skill files below.
# Rules analogue: `.trae/rules/orchestration.md`. When the agent reads this file, the intent is to
# pick the correct sub-skill (plan, backend, frontend, infra, reviewer, tester) for the task at hand.
# Do NOT add triggers / workflow steps to this file.

# Agent Skill Persona Map

Use the matching skill file to adopt the correct role & guidance before generating code:

- For planning architecture or features -> adopt persona from `.trae/skill/plan.md`
- For API/DB implementation -> adopt persona from `.trae/skill/backend.md`
- For UI/Component implementation -> adopt persona from `.trae/skill/frontend.md`
- For Docker, Nginx, Postgres/Redis/Mailpit, Makefiles, env config -> adopt persona from `.trae/skill/infra.md`
- For code reviews & quality checks -> adopt persona from `.trae/skill/reviewer.md`
- For unit & integration tests -> adopt persona from `.trae/skill/tester.md`
