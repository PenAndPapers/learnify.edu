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


fullstack-lint:
	$(MAKE) -C backend/fastapi format
	$(MAKE) -C backend/fastapi lint


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