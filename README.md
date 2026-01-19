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

### vocabulary (Vocabulary Models)

Core vocabulary models shared across the application.

**Models:**

* `Language` - Stores supported languages with code (e.g., 'en', 'hu', 'de'), name, and native language flag
* `Word` - Stores vocabulary words with language reference, word text, translation, optional definition, and timestamps

### wod (Word of the Day)

A Django app that presents users with a random word to learn in their target language, helping build vocabulary through consistent practice.

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

## Managing Vocabulary

### Admin Interface

The Django admin provides a user-friendly interface for managing languages and vocabulary words.

**Access the admin:**

1. Create a superuser (first time only): `make superuser`
2. Start the application: `make up`
3. Navigate to http://localhost:8000/admin
4. Log in with your superuser credentials

**Language Management:**

* View all languages with word counts
* Add new languages (code, name, native flag)
* Edit or delete existing languages

**Word Management:**

* Add individual words with translations
* Definition field is optional (can be added later)
* Search by word, translation, or definition
* Filter by language or date added
* View words sorted by most recent first

### Bulk Import from CSV

For adding multiple words at once, use the CSV import command.

**CSV Format:**

Create a CSV file with the following columns (first row must be headers):

```csv
language_code,word,translation,definition
hu,alma,apple,A fruit that grows on trees
hu,ház,house,
de,Buch,book,A written or printed work
de,Wasser,water,
```

**Notes on CSV format:**
* `language_code` - Required. Must match existing language (en, hu, de)
* `word` - Required. The word in the target language
* `translation` - Required. English translation
* `definition` - Optional. Can be empty, add definitions later

**Import Commands:**

```bash
# Preview import without making changes (recommended first step)
make shell
python manage.py import_words /path/to/words.csv --dry-run

# Import words for real
python manage.py import_words /path/to/words.csv

# Skip duplicate words (default behavior)
python manage.py import_words /path/to/words.csv --skip-duplicates
```

**Using Docker:**

If your CSV file is on your host machine, you need to copy it into the container or mount it:

```bash
# Option 1: Copy file into running container
docker cp words.csv django-language-web-1:/app/words.csv
docker compose exec web python manage.py import_words /app/words.csv

# Option 2: Place file in project directory (it's already mounted)
# Just put words.csv in your project root, then:
docker compose exec web python manage.py import_words /app/words.csv
```

**Import Output:**

The command provides detailed feedback:
* Success: Shows each word created/imported
* Warnings: Shows skipped duplicates
* Errors: Shows invalid rows with error messages
* Summary: Total created, skipped, and errors

**Example Output:**

```
Row 2: Created - alma → apple (hu) [with definition]
Row 3: Created - ház → house (hu)
Row 4: Skipped duplicate - Buch → book (de)
==================================================
Import Summary:
  Created: 2
  Skipped: 1
  Errors:  0
==================================================
```

**Tips for CSV Import:**

* Always run with `--dry-run` first to preview changes
* Keep a backup of your CSV file
* Start with a small test file (5-10 words) to verify format
* Definitions are optional - you can import words without them
* The command skips duplicates by default to avoid data issues

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

