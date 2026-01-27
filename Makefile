.PHONY: help up start down build rebuild logs shell test test-v test-cov lint format clean migrate makemigrations superuser collectstatic

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
	@echo "  make test            - Run all tests"
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
	@docker compose exec web pytest 2>/dev/null || docker compose run --rm web pytest

test-v:
	@docker compose exec web pytest -v 2>/dev/null || docker compose run --rm web pytest -v

test-cov:
	@docker compose exec web pytest --cov-report=html 2>/dev/null || docker compose run --rm web pytest --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@docker compose exec web black --check . 2>/dev/null || docker compose run --rm web black --check .
	@docker compose exec web isort --check-only . 2>/dev/null || docker compose run --rm web isort --check-only .
	@docker compose exec web flake8 . 2>/dev/null || docker compose run --rm web flake8 .

format:
	@docker compose exec web black . 2>/dev/null || docker compose run --rm web black .
	@docker compose exec web isort . 2>/dev/null || docker compose run --rm web isort .

# Cleanup
clean:
	docker compose down -v
	@echo "Containers and volumes removed"
