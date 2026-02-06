.PHONY: help up start down build rebuild logs shell test test-v test-cov test-ui test-all lint format clean migrate makemigrations superuser collectstatic

define RUN_IN_WEB
	@sh -c 'if [ -n "$$(docker compose ps -q web 2>/dev/null)" ]; then docker compose exec web $(1); else docker compose run --rm web $(1); fi'
endef

# Default target - show help
help:
	@echo "Django Language Learning App - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make up              - Start the application (foreground, with logs)"
	@echo "  make start           - Start the application (background/detached)"
	@echo "  make down            - Stop the application"
	@echo "  make build           - Build and start (first time or after Dockerfile changes)"
	@echo "  make rebuild         - Rebuild containers from scratch"
	@echo "  make logs            - View application logs (follow mode)"
	@echo ""
	@echo "Django Management:"
	@echo "  make shell           - Open Django shell"
	@echo "  make migrate         - Run database migrations"
	@echo "  make makemigrations  - Create new migrations"
	@echo "  make superuser       - Create a superuser"
	@echo "  make collectstatic   - Collect static files"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test            - Run unit tests (excludes playwright)"
	@echo "  make test-ui         - Run only playwright UI tests"
	@echo "  make test-all        - Run all tests including playwright"
	@echo "  make test-v          - Run tests with verbose output"
	@echo "  make test-cov        - Run tests with HTML coverage report"
	@echo "  make lint            - Run flake8 linter"
	@echo "  make format          - Format code with black and isort"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           - Remove containers and volumes"

# Development commands
up:
	docker compose up

start:
	docker compose up -d
	@echo "Application started in background. Use 'make logs' to view logs."

down:
	docker compose down

build:
	docker compose up --build

rebuild:
	docker compose down -v
	docker compose build --no-cache
	docker compose up

logs:
	docker compose logs -f

# Django management commands
shell:
	@docker compose exec web python manage.py shell 2>/dev/null || docker compose run --rm web python manage.py shell

migrate:
	@docker compose exec web python manage.py migrate 2>/dev/null || docker compose run --rm web python manage.py migrate

makemigrations:
	@docker compose exec web python manage.py makemigrations 2>/dev/null || docker compose run --rm web python manage.py makemigrations

superuser:
	@docker compose exec web python manage.py createsuperuser 2>/dev/null || docker compose run --rm web python manage.py createsuperuser

collectstatic:
	@docker compose exec web python manage.py collectstatic --noinput 2>/dev/null || docker compose run --rm web python manage.py collectstatic --noinput

# Testing and code quality
test:
	$(call RUN_IN_WEB,pytest)

test-ui:
	poetry run pytest -m playwright --no-cov

test-all:
	poetry run pytest -m "" --no-cov

test-v:
	$(call RUN_IN_WEB,pytest -v)

test-cov:
	$(call RUN_IN_WEB,pytest --cov-report=html)
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	$(call RUN_IN_WEB,black --check .)
	$(call RUN_IN_WEB,isort --check-only .)
	$(call RUN_IN_WEB,flake8 .)

format:
	$(call RUN_IN_WEB,black .)
	$(call RUN_IN_WEB,isort .)

# Cleanup
clean:
	docker compose down -v
	@echo "Containers and volumes removed"
