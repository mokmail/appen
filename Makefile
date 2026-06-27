# ============================================================================
#  BEV KI-Plattform — Makefile
#  All available commands for the SvelteKit frontend, FastAPI backend,
#  Docker deployments, testing, linting, formatting, and tooling.
# ============================================================================

# --- Docker compose binary detection -----------------------------------------
ifneq ($(shell which docker-compose 2>/dev/null),)
    DOCKER_COMPOSE := docker-compose
else
    DOCKER_COMPOSE := docker compose
endif

# --- Default port / image ----------------------------------------------------
PORT        ?= 3000
BACKEND_PORT ?= 8080
IMAGE       ?= open-webui
CONTAINER   ?= open-webui
OVERLAY_IMAGE   ?= open-webui-overlay
OVERLAY_CONTAINER ?= open-webui-overlay

# --- Colors ------------------------------------------------------------------
BOLD   := \033[1m
GREEN  := \033[1;32m
YELLOW := \033[1;33m
CYAN   := \033[1;36m
RESET  := \033[0m

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@echo ""
	@echo "$(BOLD)BEV KI-Plattform$(RESET) — available commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_][a-zA-Z0-9_-]+:.*?## / { printf "  $(CYAN)%-22s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Tip$(RESET): most frontend commands run via npm; most backend commands run via uv/uvicorn."
	@echo ""

# ============================================================================
#  FRONTEND (SvelteKit + Vite + Tailwind v4)
# ============================================================================

.PHONY: dev dev-5050 build build-watch preview pyodide-fetch
dev: ## Start Vite dev server (host enabled, port 5173)
	npm run dev

dev-5050: ## Start Vite dev server on port 5050
	npm run dev:5050

build: ## Production build — reads WEBUI_VERSION from .env so frontend matches backend
	npm run build

build-watch: ## Build in watch mode
	npm run build:watch

preview: ## Preview the production build locally
	npm run preview

pyodide-fetch: ## Fetch Pyodide assets (runs automatically before dev/build)
	npm run pyodide:fetch

# ============================================================================
#  LINTING & TYPE CHECKING
# ============================================================================

.PHONY: lint lint-frontend lint-types lint-backend format format-backend
lint: ## Run all linters (frontend + types + backend)
	npm run lint

lint-frontend: ## Lint & auto-fix frontend (eslint)
	npm run lint:frontend

lint-types: ## Type-check the frontend (svelte-check)
	npm run lint:types

lint-backend: ## Lint the backend (pylint)
	npm run lint:backend

format: ## Format frontend code (prettier)
	npm run format

format-backend: ## Format backend code (ruff)
	npm run format:backend

.PHONY: check check-watch
check: ## Type-check the frontend (alias for lint:types)
	npm run check

check-watch: ## Type-check in watch mode
	npm run check:watch

# ============================================================================
#  TESTING
# ============================================================================

.PHONY: test-frontend cy-open test-e2e
test-frontend: ## Run frontend unit tests (vitest)
	npm run test:frontend

cy-open: ## Open Cypress interactive runner
	npm run cy:open

test-e2e: ## Run Cypress e2e tests headless
	npx cypress run

# ============================================================================
#  I18N
# ============================================================================

.PHONY: i18n-parse
i18n-parse: ## Parse & extract i18n strings, then prettier-write the output
	npm run i18n:parse

# ============================================================================
#  ICONS (Lucide wrapper generator — Kartografisch design system)
# ============================================================================

.PHONY: icons-generate
icons-generate: ## Regenerate Lucide icon wrappers from the name map
	node scripts/generate-lucide-icons.cjs

.PHONY: bev-assets-overlay
bev-assets-overlay: ## Re-apply BEV branding assets onto upstream static dirs (run after upgrade)
	@bash scripts/bev-asset-overlay.sh

# ============================================================================
#  BACKEND (FastAPI / Uvicorn)
# ============================================================================

.PHONY: backend-dev backend-start backend-install backend-install-all
backend-dev: ## Start backend in reload mode (uvicorn, port 8080)
	cd backend && ./dev.sh

backend-start: ## Start backend in production mode (uvicorn workers)
	cd backend && ./start.sh

backend-install: ## Install backend dependencies via uv
	uv sync

backend-install-all: ## Install backend + all optional extras (postgres, mariadb, unstructured, dev)
	uv sync --all-extras

# ============================================================================
#  DOCKER — full stack (Open WebUI + Ollama)
# ============================================================================

.PHONY: install start stop restart startAndBuild update remove
install: ## Build & start the full stack in the background
	$(DOCKER_COMPOSE) up -d

start: ## Start existing containers
	$(DOCKER_COMPOSE) start

stop: ## Stop running containers
	$(DOCKER_COMPOSE) stop

restart: ## Restart the full stack
	$(DOCKER_COMPOSE) restart

startAndBuild: ## Rebuild images then start the stack
	$(DOCKER_COMPOSE) up -d --build

update: ## Pull latest, rebuild, and restart (also updates Ollama models)
	chmod +x update_ollama_models.sh
	@./update_ollama_models.sh
	@git pull
	$(DOCKER_COMPOSE) down
	@docker stop open-webui || true
	$(DOCKER_COMPOSE) up --build -d
	$(DOCKER_COMPOSE) start

remove: ## Remove all containers & volumes (prompts for confirmation)
	@chmod +x confirm_remove.sh
	@./confirm_remove.sh

.PHONY: logs logs-backend logs-ollama
logs: ## Tail logs for all services
	$(DOCKER_COMPOSE) logs -f --tail=200

logs-backend: ## Tail open-webui logs only
	$(DOCKER_COMPOSE) logs -f --tail=200 open-webui

logs-ollama: ## List host Ollama models (Ollama runs on host, not in compose)
	ollama list 2>/dev/null || echo "Ollama not found on host"

.PHONY: down down-volumes
down: ## Stop & remove containers (keeps volumes)
	$(DOCKER_COMPOSE) down

down-volumes: ## Stop & remove containers AND volumes (data loss!)
	$(DOCKER_COMPOSE) down -v

# ============================================================================
#  DOCKER — alternate compose profiles
# ============================================================================

.PHONY: bev bev-overlay gpu amdgpu data api a1111 oikb otel playwright
bev: ## Start the BEV in-house profile (builds from source Dockerfile)
	$(DOCKER_COMPOSE) -f docker-compose.bev.yaml up -d --build

bev-overlay: ## Start BEV using the overlay image (Dockerfile.overlay, no source build)
	$(DOCKER_COMPOSE) -f docker-compose.bev.yaml -f docker-compose.bev.overlay.yaml up -d --build

gpu: ## Start with NVIDIA GPU support
	$(DOCKER_COMPOSE) -f docker-compose.gpu.yaml up -d --build

amdgpu: ## Start with AMD GPU support
	$(DOCKER_COMPOSE) -f docker-compose.amdgpu.yaml up -d --build

data: ## Start the data-services profile
	$(DOCKER_COMPOSE) -f docker-compose.data.yaml up -d

api: ## Start the API-only profile
	$(DOCKER_COMPOSE) -f docker-compose.api.yaml up -d

a1111: ## Start the A1111 test profile
	$(DOCKER_COMPOSE) -f docker-compose.a1111-test.yaml up -d

oikb: ## Start the OIKB profile
	$(DOCKER_COMPOSE) -f docker-compose.oikb.yaml up -d

oikb-sync: ## Trigger an OIKB sync inside the running oikb container
	docker exec -it oikb oikb sync

otel: ## Start the OpenTelemetry observability profile
	$(DOCKER_COMPOSE) -f docker-compose.otel.yaml up -d

playwright: ## Start the Playwright browser profile
	$(DOCKER_COMPOSE) -f docker-compose.playwright.yaml up -d

# ============================================================================
#  DOCKER — single container (no compose)
# ============================================================================

.PHONY: docker-build docker-build-overlay docker-run docker-run-overlay docker-stop docker-rm
docker-build: ## Build the standalone Docker image (from source Dockerfile, slim for CPU)
	docker build --build-arg USE_SLIM=true -t $(IMAGE) .

docker-build-overlay: ## Build the overlay image on top of the official release (Dockerfile.overlay)
	@READ_TAG=$${OPEN_WEBUI_TAG:-main}; \
	docker build -f Dockerfile.overlay \
		--build-arg OPEN_WEBUI_TAG=$$READ_TAG \
		-t $(OVERLAY_IMAGE):$$READ_TAG .

docker-run: ## Run the standalone container on port $(PORT)
	docker stop $(CONTAINER) 2>/dev/null || true
	docker rm $(CONTAINER) 2>/dev/null || true
	docker run -d -p $(PORT):8080 \
		--add-host=host.docker.internal:host-gateway \
		-v $(IMAGE):/app/backend/data \
		--name $(CONTAINER) --restart always $(IMAGE)
	docker image prune -f

docker-run-overlay: ## Run the overlay container on port $(PORT)
	@READ_TAG=$${OPEN_WEBUI_TAG:-main}; \
	docker stop $(OVERLAY_CONTAINER) 2>/dev/null || true; \
	docker rm $(OVERLAY_CONTAINER) 2>/dev/null || true; \
	docker run -d -p $(PORT):8080 \
		--add-host=host.docker.internal:host-gateway \
		-v $(OVERLAY_IMAGE):/app/backend/data \
		--name $(OVERLAY_CONTAINER) --restart always $(OVERLAY_IMAGE):$$READ_TAG; \
	docker image prune -f

docker-stop: ## Stop the standalone container
	docker stop $(CONTAINER) || true

docker-rm: ## Remove the standalone container
	docker rm $(CONTAINER) || true

# ============================================================================
#  OLLAMA
# ============================================================================

.PHONY: ollama-docker ollama-models ollama-serve
ollama-docker: ## Run Ollama in Docker (prompts for GPU support)
	@chmod +x run-ollama-docker.sh
	@./run-ollama-docker.sh

ollama-models: ## Update all installed Ollama models
	@chmod +x update_ollama_models.sh
	@./update_ollama_models.sh

ollama-serve: ## Start a local Ollama server
	ollama serve

# ============================================================================
#  SBOM (Software Bill of Materials)
# ============================================================================

.PHONY: sbom sbom-docker sbom-validate
sbom: ## Generate a CycloneDX SBOM from resolved manifests
	@./scripts/generate-sbom.sh generate

sbom-docker: ## Generate SBOM from the Docker image
	@./scripts/generate-sbom.sh docker

sbom-validate: ## Validate the existing SBOM
	@./scripts/generate-sbom.sh validate

# ============================================================================
#  GIT & PRE-COMMIT
# ============================================================================

.PHONY: precommit
precommit: ## Run pre-commit hooks on all files (ruff + ruff-format on backend)
	pre-commit run --all-files

# ============================================================================
#  CLEANUP
# ============================================================================

.PHONY: clean clean-frontend clean-docker
clean: clean-frontend clean-docker ## Clean everything (build artefacts + Docker)

clean-frontend: ## Remove frontend build artefacts & caches
	rm -rf .svelte-kit node_modules/.vite dist

clean-docker: ## Remove dangling Docker images & stopped containers
	docker image prune -f
	docker container prune -f