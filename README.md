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

## Status

Currently in initial development phase. Docker containerization and detailed setup instructions will be added in upcoming changes.
