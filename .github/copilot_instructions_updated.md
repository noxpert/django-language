# GitHub Copilot Instructions for django-language

## Project Overview
Django language learning app supporting English, Hungarian, and German. Goals: AI-assisted development, technology stack mastery (Django/Python/Poetry/Docker), and building a practical language learning tool.

## Tech Stack
- Django 5.2.8, Python 3.14, Poetry 2.1.3
- **No virtual environments**: Poetry configured with `virtualenvs.create = false`
- Docker (`python:3.14-slim`), no virtualenvs in containers (`POETRY_VIRTUALENVS_CREATE=false`)
- Neon PostgreSQL (external, connected via `DATABASE_URL`)
- Deployed on Render (free web services)
- Auth0 for authentication (via django-allauth)
- Django i18n for internationalization
- MIT licensed

## Project Structure
```
django-language/
├── djangolanguage/         # Project settings, urls, wsgi
├── vocabulary/             # Shared models: Language, Word, Translation
│   ├── models.py           # Core data models
│   ├── admin.py            # Admin with TranslationInline
│   ├── migrations/         # Includes data migrations for initial + family words
│   └── management/commands/
│       └── import_words.py # CSV import with Translation support
├── wod/                    # Word of the Day app
├── match/                  # Word matching exercise app
├── static/                 # Static files (favicon.svg)
├── Makefile                # Development command shortcuts
├── Dockerfile
├── docker-compose.yml
├── .clainerules            # Context file for Claude AI
└── pyproject.toml
```

## Data Models

### Language
- `code` (unique, e.g., 'en', 'hu', 'de')
- `name`

### Word
- `language` (FK → Language)
- `word` (text of the word)
- `definition` (in the same language as the word)
- Custom manager with `random_word(lang_code)`, `random_words(lang_code, count)`, `for_language(lang_code)`
- Helper methods: `get_translations()`, `get_translation(lang_code)`, `has_translation_to(lang_code)`

### Translation (Junction Table)
- `source_word` (FK → Word)
- `target_word` (FK → Word)
- `confidence` (exact, close, approximate)
- `notes`
- Bidirectional: if A→B exists, queries work from both directions
- Validation: source and target must be different languages

## Apps

### vocabulary
Shared data layer. Owns Language, Word, and Translation models. All other apps import from here.

### wod (Word of the Day)
Displays a random word in a selected language with its English translation.
- Language selector only shows languages that have words (uses `annotate/Count`)
- Uses `Word.objects.random_words()` manager method

### match
Word matching exercise. Users match words with translations.
- Configurable 2-10 words per exercise
- Language selector, shuffled translations
- Click-to-match UI, check answers, score display
- Models: `MatchSession`, `Match`
- JSON API endpoint for checking matches (`/match/check/`)

## Authentication
- Auth0 via django-allauth
- Separate Auth0 app configurations for localhost and Render
- Secrets managed via Render environment variables
- Callback URL: `/accounts/auth0/login/callback/`

## Development Workflow

### Docker (Preferred)
```bash
make up          # Start (foreground)
make start       # Start (background)
make down        # Stop
make build       # First run or after Dockerfile changes
make test        # Run tests (excludes UI tests)
make test-ui     # Run only UI tests (Playwright)
make test-all    # Run all tests including UI tests
make shell       # Django shell
make migrate     # Run migrations
make lint        # Flake8
make format      # Black + isort
```

### Poetry (Local)
- Use modern syntax: `--without dev` (never `--no-dev`)
- Add deps: `poetry add <pkg>` / `poetry add --group dev <pkg>`

## Code Quality
- **Black** for formatting
- **Flake8** for linting (config in `.flake8`)
- **isort** for import sorting
- **pytest** for testing (config in `pytest.ini`)
- Run before committing: `make format && make lint && make test`

## Testing
- Unit tests: pytest with Django TestCase
- Test files organized per app
- Tests cover models, views, admin, management commands
- UI tests: Playwright with pytest (`pytest-playwright`)
- UI tests marked with `@pytest.mark.ui` marker
- Test with Docker: `docker compose exec web pytest`
- Run only UI tests: `make test-ui`
- Run all tests including UI: `make test-all`
- Default `make test` excludes UI tests for faster iteration

### UI Testing with Playwright
- UI test files: `test_ui*.py` in each app directory
- All UI tests decorated with `@pytest.mark.ui` marker
- **Graceful degradation**: UI tests automatically skipped if Playwright not installed
- Use `pytest.importorskip("playwright.sync_api")` at module level
- Use `live_server` fixture for Django integration
- Tests run against live Django server in test mode
- Playwright browsers: Chromium (primary), Firefox, WebKit
- UI tests cover: page loads, user interactions, form submissions, navigation
- Test files:
  - `wod/test_ui.py` - Word of the Day UI tests
  - `exercises/test_ui_matching.py` - Matching exercise UI tests
  - `exercises/test_ui_spelling.py` - Spelling exercise UI tests
- Playwright browsers installed automatically in Docker (after rebuild)
- For local development: `poetry run playwright install chromium`
- Dockerfile includes Playwright system dependencies

## Deployment

### Render
- Web services (free tier, sleeps when inactive)
- Environment variables for all secrets (not secret files)
- Auto-deploys from main branch via GitHub Actions
- `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` configured for Render domain

### Database
- Neon PostgreSQL (external, free tier)
- Connected via `DATABASE_URL` environment variable
- Scale-to-zero when idle
- Local development can use SQLite as fallback

### Secrets (Render Environment Variables)
- `DATABASE_URL` - Neon connection string
- `AUTH0_DOMAIN`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `DJANGO_SECRET_KEY`
- `ALLOWED_HOSTS`

## Django Conventions
- i18n: Use `gettext_lazy` for user-facing text
- Templates: Organize by app, use template inheritance
- Models: Include timestamps, `__str__` methods, proper FKs
- URLs: Namespaced per app (`app_name`)
- Static files: `{% load static %}` and `{% static %}` tags

## Import Words CLI
```bash
# Basic import
python manage.py import_words data.csv

# Options
--dry-run              # Preview without importing
--skip-duplicates      # Skip existing words
--target-language=en   # Translation target (default: en)
--bidirectional        # Create translations both ways
--confidence=exact     # Translation confidence level
```

## Copilot Guidelines
- Follow Django conventions and project structure
- Use the vocabulary app models for any word/language data
- Definitions should be in the same language as the word
- Use Translation model to link words across languages
- Include tests for new features
- Run format/lint checks on generated code
- Consider i18n for user-facing strings
- Use Makefile commands for development tasks

## Recent Changes (January 2026)

### No Virtual Environment Configuration
- Configured Poetry to not create virtual environments (`virtualenvs.create = false`)
- Simplifies local development workflow
- Consistent with Docker container behavior
- See `TESTING_WITHOUT_VENV.md` for details

### Playwright UI Testing Setup
- Added `pytest-playwright` and `playwright` to dev dependencies
- Created UI test marker `@pytest.mark.ui` in pytest.ini
- **Graceful skipping**: UI tests skip automatically if Playwright not installed (no import errors)
- Created three UI test suites:
  - `wod/test_ui.py` - 11 tests for Word of the Day page
  - `exercises/test_ui_matching.py` - 10 tests for Matching exercise
  - `exercises/test_ui_spelling.py` - 10 tests for Spelling exercise
- Updated Makefile with new commands:
  - `make test` - Now excludes UI tests for faster iteration
  - `make test-ui` - Run only Playwright UI tests
  - `make test-all` - Run all tests including UI
- Updated Dockerfile with Playwright system dependencies and browser installation
- Updated CI/CD workflow to run UI tests separately
- Created `conftest.py` with Playwright fixtures (`live_server`, `page`)
- Updated documentation (README.md, copilot_instructions_updated.md)
- Created PLAYWRIGHT_SETUP.md with comprehensive setup guide
- Created TESTING_WITHOUT_VENV.md for local development guide
