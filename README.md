# django-language

## Purpose

This project serves three learning objectives:

* **AI-Assisted Development**: Learning to work effectively with AI tools in software development
* **Technology Stack**: Gaining hands-on experience with Django, Python, Poetry, and Docker
* **Language Learning**: Building an application to support learning and practicing human languages (English, Hungarian, and German)

## Technology Stack

* **Framework**: Django 5.2.8
* **Language**: Python 3.14
* **Dependency Management**: Poetry 2.1.3
* **Containerization**: Docker
  + Base image: `python:3.14-slim`
* **Internationalization**: Django's built-in i18n framework

## Supported Languages

The application will support multiple languages:

* English
* Hungarian
* German

## Apps

### wod (Word of the Day)

A Django app that presents users with a daily word to learn in their target language, helping build vocabulary through consistent daily practice.

**Models:**

* `Language` - Stores supported languages with code (e.g., 'en', 'hu', 'de'), name, and native language flag
* `Word` - Stores vocabulary words with language reference, translation, definition, and timestamps

## Quick Start with Docker

The easiest way to run this project is using Docker and the provided Makefile:

```bash
# First time setup - build and start
make build

# Start in foreground (with logs visible)
make up

# Or start in background (detached mode)
make start

# View logs (when running in background)
make logs

# Stop the application
make down
```

Access the application at http://localhost:8000

## Makefile Commands

The project includes a Makefile to simplify common development tasks. Run `make help` to see all available commands:

### Development

* `make up` - Start the application (foreground, with logs)
* `make start` - Start the application (background/detached)
* `make down` - Stop the application
* `make build` - Build and start (first time or after Dockerfile changes)
* `make rebuild` - Rebuild containers from scratch
* `make logs` - View application logs (follow mode)

### Django Management

* `make shell` - Open Django shell
* `make migrate` - Run database migrations
* `make makemigrations` - Create new migrations
* `make superuser` - Create a superuser
* `make collectstatic` - Collect static files

### Testing & Quality

* `make test` - Run all tests
* `make test-v` - Run tests with verbose output
* `make test-cov` - Run tests with HTML coverage report (see `htmlcov/index.html`)
* `make lint` - Run flake8 linter
* `make format` - Format code with black and isort

### Cleanup

* `make clean` - Remove containers and volumes

## Development Commands (Alternative)

If you prefer not to use the Makefile, you can run commands directly:

### Docker

* `docker compose up` - Start containers
* `docker compose up --build` - Build and start
* `docker compose down` - Stop containers
* `docker compose logs -f` - View logs
* `docker compose exec web python manage.py <command>` - Run Django commands
* `docker compose exec web python manage.py shell` - Open Django shell
* `docker compose exec web pytest` - Run tests inside container

### Poetry (Local Development)

* `poetry install` - Install dependencies
* `poetry add <package>` - Add new package
* `poetry add --group dev <package>` - Add dev dependency
* `poetry run python manage.py <command>` - Run Django commands
* `poetry shell` - Activate virtual environment

### Linting & Formatting

* `poetry run black .` - Format code
* `poetry run flake8 .` - Lint code
* `poetry run isort .` - Sort imports

### Testing

* `poetry run pytest` - Run all tests with coverage report
* `poetry run pytest wod/` - Run tests for specific app
* `poetry run pytest -v` - Run tests with verbose output
* `poetry run pytest --lf` - Run only last failed tests
* `poetry run pytest --cov-report=html` - Generate HTML coverage report

## Docker Setup Details

The project is fully Dockerized for consistent development environments:

* Poetry installs packages directly to system Python (no virtual environments in containers)
* Environment variable `POETRY_VIRTUALENVS_CREATE=false` ensures this behavior
* Volume mounting allows live code updates without rebuilding
* Port 8000 is exposed for the Django development server

## Status

Currently in active development. Core features and infrastructure are in place.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

