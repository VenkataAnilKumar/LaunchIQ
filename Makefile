.PHONY: dev local local-celery local-down local-status test eval eval-live migrate seed demo

# --- Full stack with Docker (Postgres + Redis + Qdrant) ---
dev:
	docker-compose up -d
	pnpm install
	cd src/apps/web && pnpm dev

# --- Keyless local stack: fake LLM + fake search + SQLite + local Redis (no Docker, no API keys) ---
local:
	scripts/local_stack.sh up inline
	@echo "Web: cd src/apps/web && NEXT_PUBLIC_DEV_BEARER_TOKEN=$$(python3 scripts/dev_token.py) pnpm dev"

local-celery:
	scripts/local_stack.sh up celery

local-down:
	scripts/local_stack.sh down

local-status:
	scripts/local_stack.sh status

test:
	pytest src/ --cov=src --cov-report=term-missing

# Offline gate: real agents + fake LLM over the brief corpus (no keys). `eval-live` needs ANTHROPIC_API_KEY.
eval:
	python src/evals/regression/run_regression.py --offline --assert-baseline

eval-live:
	python src/evals/regression/run_regression.py

migrate:
	cd src/memory/structured && alembic upgrade head

seed:
	python src/data/seed.py --demo

demo:
	$(MAKE) migrate
	$(MAKE) seed
	$(MAKE) dev
