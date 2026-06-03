.PHONY: backend-fastapi-install backend-fastapi-update backend-fastapi-up backend-fastapi-down

PROJECT_NAME := learnify_edu

# ==============================================================================
# Fastapi Docker Operations
# ==============================================================================

backend-fastapi-install:
	$(MAKE) -C backend/fastapi install

backend-fastapi-update:
	$(MAKE) -C backend/fastapi update-deps

backend-fastapi-build:
	$(MAKE) -C backend/fastapi docker-build

backend-fastapi-up:
	$(MAKE) -C backend/fastapi docker-up

backend-fastapi-down:
	$(MAKE) -C backend/fastapi docker-down

backend-fastapi-down-v:
	$(MAKE) -C backend/fastapi docker-down-v


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


# ==============================================================================
# Fullstack Operations
# ==============================================================================

# Run this to boot up the backend containers and spin up the native Nuxt UI server simultaneously
fullstack-up:
	@echo "🌐 Starting core backend infrastructure..."
	$(MAKE) backend-fastapi-up
	@echo "🎨 Launching local Nuxt 4 dev workspace..."
	$(MAKE) frontend-nuxt-dev

# Run this to shut down all running backend infrastructure cleanly
fullstack-down:
	$(MAKE) backend-fastapi-down


# ==============================================================================
# Docker Operations
# ==============================================================================

docker-build:
	docker-compose build --parallel --no-cache

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down --remove-orphans

docker-down-v:
	docker-compose down -v --remove-orphans

docker-restart:
	$(MAKE) docker-down
	$(MAKE) docker-up

clean-all:
	docker compose down -v --remove-orphans
	docker system prune -a --volumes --force