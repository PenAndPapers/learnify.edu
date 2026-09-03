.PHONY: \
        backend-fastapi-install backend-fastapi-update backend-fastapi-clean \
        backend-fastapi-up backend-fastapi-down backend-fastapi-down-v backend-fastapi-restart backend-fastapi-build backend-fastapi-lint \
        backend-fastapi-test backend-fastapi-test-unit backend-fastapi-test-integration backend-fastapi-test-e2e \
        backend-fastapi-migration backend-fastapi-migrate backend-fastapi-migrate-down backend-fastapi-migrate-logs backend-fastapi-migrate-check \
        frontend-nuxt-install-deps frontend-nuxt-update-deps frontend-nuxt-build frontend-nuxt-dev frontend-nuxt-generate frontend-nuxt-preview frontend-nuxt-postinstall \
        frontend-nuxt-full-fix frontend-nuxt-test \
        frontend-nuxt-lint frontend-nuxt-lint-fix frontend-nuxt-format frontend-nuxt-format-check frontend-nuxt-typecheck \
        fullstack-up fullstack-down fullstack-lint fullstack-test \
        hooks-install hooks-uninstall \
        docker-clean-all

PROJECT_NAME := learnify_edu

# Pin compose file + project name so all wrappers resolve the same stack
# regardless of caller CWD, stray compose.*.yml files, or env overrides.
COMPOSE_FILE ?= $(abspath $(CURDIR)/docker-compose.yml)
COMPOSE_PROJECT_NAME ?= learnifyedu
export COMPOSE_FILE
export COMPOSE_PROJECT_NAME

# ==============================================================================
# Fastapi Docker Operations
# ==============================================================================

backend-fastapi-install:
	$(MAKE) -C backend/fastapi install

backend-fastapi-update:
	$(MAKE) -C backend/fastapi update-deps

backend-fastapi-clean:
	$(MAKE) -C backend/fastapi clean

backend-fastapi-up:
	$(MAKE) -C backend/fastapi docker-up

backend-fastapi-down:
	$(MAKE) -C backend/fastapi docker-down

backend-fastapi-down-v:
	$(MAKE) -C backend/fastapi docker-down-v

backend-fastapi-restart:
	$(MAKE) -C backend/fastapi docker-restart

backend-fastapi-build:
	$(MAKE) -C backend/fastapi docker-build

backend-fastapi-lint:
	$(MAKE) -C backend/fastapi format
	$(MAKE) -C backend/fastapi lint

# ==============================================================================
# Fastapi Test Operations
# ==============================================================================

backend-fastapi-test:
	$(MAKE) -C backend/fastapi test

backend-fastapi-test-unit:
	$(MAKE) -C backend/fastapi test-unit

backend-fastapi-test-integration:
	$(MAKE) -C backend/fastapi test-integration

backend-fastapi-test-e2e:
	$(MAKE) -C backend/fastapi test-e2e

# ==============================================================================
# Fastapi Migration Operations
# ==============================================================================

backend-fastapi-migration:
	$(MAKE) -C backend/fastapi migration

backend-fastapi-migrate:
	$(MAKE) -C backend/fastapi migrate

backend-fastapi-migrate-down:
	$(MAKE) -C backend/fastapi migrate-down

backend-fastapi-migrate-logs:
	$(MAKE) -C backend/fastapi migrate-logs

backend-fastapi-migrate-check:
	$(MAKE) -C backend/fastapi migrate-check


# ==============================================================================
# Nuxt Operations
# ==============================================================================

frontend-nuxt-install-deps:
	$(MAKE) -C frontend/nuxt4 install-deps

frontend-nuxt-update-deps:
	$(MAKE) -C frontend/nuxt4 update-deps

frontend-nuxt-build:
	$(MAKE) -C frontend/nuxt4 build

frontend-nuxt-dev:
	$(MAKE) -C frontend/nuxt4 dev

frontend-nuxt-generate:
	$(MAKE) -C frontend/nuxt4 generate

frontend-nuxt-preview:
	$(MAKE) -C frontend/nuxt4 preview

frontend-nuxt-postinstall:
	$(MAKE) -C frontend/nuxt4 postinstall

frontend-nuxt-full-fix:
	$(MAKE) -C frontend/nuxt4 full-fix

frontend-nuxt-test:
	$(MAKE) -C frontend/nuxt4 test

frontend-nuxt-lint:
	$(MAKE) -C frontend/nuxt4 lint

frontend-nuxt-lint-fix:
	$(MAKE) -C frontend/nuxt4 lint-fix

frontend-nuxt-format:
	$(MAKE) -C frontend/nuxt4 format

frontend-nuxt-format-check:
	$(MAKE) -C frontend/nuxt4 format-check

frontend-nuxt-typecheck:
	$(MAKE) -C frontend/nuxt4 typecheck


# ==============================================================================
# Fullstack Operations
# ==============================================================================

# Run this to boot up the backend containers and spin up the native Nuxt UI server simultaneously for local development
fullstack-up:
	@echo "🌐 Starting core backend infrastructure..."
	$(MAKE) backend-fastapi-up
	@echo "🎨 Launching local Nuxt 4 dev workspace..."
	$(MAKE) frontend-nuxt-dev

# Run this to shut down all running backend infrastructure cleanly
fullstack-down:
	$(MAKE) backend-fastapi-down

# Run this to lint the backend code.
fullstack-lint:
	$(MAKE) backend-fastapi-lint
	$(MAKE) frontend-nuxt-lint

# Run application full test (backend first → fail-fast on infra)
fullstack-test:
	@echo
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "  Backend FastAPI tests — gateway + api + database must be up  "
	@echo "  (run 'make backend-fastapi-up' first if containers are down) "
	@echo "═══════════════════════════════════════════════════════════════"
	$(MAKE) backend-fastapi-test
	@echo
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "  Frontend Nuxt 4 Vitest suite                                  "
	@echo "═══════════════════════════════════════════════════════════════"
	$(MAKE) frontend-nuxt-test

# ==============================================================================
# Git Hooks (Local Dev Quality Gates — Devs install once per clone)
# ==============================================================================

hooks-install:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-commit .githooks/pre-push
	@echo
	@echo "✅ Git hooks installed -> repository '.githooks/' directory."
	@echo "   - pre-commit : frontend full:fix auto-apply (blocks on failure),"
	@echo "                 backend format if api container is up (warns if down)."
	@echo "   - pre-push   : frontend format-check + lint + typecheck + Vitest,"
	@echo "                 backend lint + pytest (requires running containers)."
	@echo "   Bypass (emergency only):  git commit|push --no-verify"
	@echo

hooks-uninstall:
	git config --unset core.hooksPath || true
	@echo
	@echo "🧹 Git hooks uninstalled (core.hooksPath removed — reverted to default .git/hooks/)."
	@echo

# ==============================================================================
# Docker Operations
# ==============================================================================

docker-clean-all:
# 1. Try standard compose down first
	-docker compose down -v --remove-orphans

	# 2. Force-remove any remaining containers matching "learnifyedu"
	@echo "Force clearing any remaining learnifyedu containers..."
	@containers=$$(docker ps -a --filter "name=learnifyedu" -q); \
	if [ ! -z "$$containers" ]; then \
		docker rm -f $$containers; \
	fi

	# 3. Clear out any leftover networks matching "learnifyedu"
	@echo "Removing learnifyedu networks..."
	@networks=$$(docker network ls --filter "name=learnifyedu" -q); \
	if [ ! -z "$$networks" ]; then \
		docker network rm $$networks 2>/dev/null || true; \
	fi

	# 4. Safely remove images belonging to the project
	@echo "Cleaning up learnifyedu images..."
	@images=$$(docker images --filter "reference=learnifyedu*" -q); \
	if [ ! -z "$$images" ]; then \
		docker rmi -f $$images; \
	else \
		echo "No learnifyedu images found."; \
	fi