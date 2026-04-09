dev:
	docker-compose up -d
	pnpm install
	cd src/apps/web && pnpm dev

test:
	pytest src/ --cov=src --cov-report=term-missing

eval:
	python src/evals/regression/run_regression.py --offline

migrate:
	cd src/memory/structured && alembic upgrade head

seed:
	python src/data/seed.py --demo

demo:
	$(MAKE) migrate
	$(MAKE) seed
	$(MAKE) dev
