# django-language

## Purpose

This project serves three learning objectives:
- **AI-Assisted Development**: Learning to work effectively with AI tools in software development
- **Technology Stack**: Gaining hands-on experience with Django, Python, Poetry, and Docker
- **Language Learning**: Building an application to support learning and practicing human languages (English, Hungarian, and German)

## Technology Stack

- **Framework**: Django 5.2.8
- **Language**: Python 3.14
- **Dependency Management**: Poetry 2.1.3
- **Containerization**: Docker (planned)
  - Base image: `python:3.14-slim`
- **Internationalization**: Django's built-in i18n framework

## Supported Languages

The application will support multiple languages:
- English
- Hungarian
- German

## Apps

### wod (Word of the Day)
A Django app that presents users with a daily word to learn in their target language, helping build vocabulary through consistent daily practice.

**Models:**
- `Language` - Stores supported languages with code (e.g., 'en', 'hu', 'de'), name, and native language flag
- `Word` - Stores vocabulary words with language reference, translation, definition, and timestamps

## Development Commands

### Poetry
- `poetry install` - Install dependencies
- `poetry add <package>` - Add new package
- `poetry add --group dev <package>` - Add dev dependency
- `poetry run python manage.py <command>` - Run Django commands
- `poetry shell` - Activate virtual environment

### Linting & Formatting
- `poetry run black .` - Format code
- `poetry run flake8 .` - Lint code
- `poetry run isort .` - Sort imports

### Testing
- `poetry run pytest` - Run all tests with coverage report
- `poetry run pytest wod/` - Run tests for specific app
- `poetry run pytest -v` - Run tests with verbose output
- `poetry run pytest --lf` - Run only last failed tests
- `poetry run pytest --cov-report=html` - Generate HTML coverage report (see htmlcov/index.html)

### Docker
The most common workflow is: 

`docker compose up --build` - (first time)

`docker compose up` - to start

`docker compose down` - when you're done

#### Examples
- `docker compose up --build` - Build and run containers (first time or after Dockerfile changes)
- `docker compose up` - Run development server
- `docker compose up -d` - Run containers in detached mode (runs in background)
- `docker compose down` - Stop containers
- `docker compose down -v` - Stop and remove volumes (removes database data)
- `docker compose logs` - View logs from all services
- `docker compose logs -f` - Follow logs in real-time
- `docker compose logs web` - View logs for specific service
- `docker compose exec web poetry run python manage.py <command>` - Run Django management commands
- `docker compose exec web poetry run python manage.py migrate` - Apply database migrations
- `docker compose exec web poetry run python manage.py createsuperuser` - Create admin user
- `docker compose exec web poetry run python manage.py shell` - Open Django shell
- `docker compose exec web poetry run pytest` - Run tests inside container
- `docker compose exec web sh` - Open shell inside web container
- `docker compose ps` - List running containers
- `docker compose restart web` - Restart web service

## Status

Currently in early development phase.
