# Testing Without Virtual Environments

## Current Setup

The project is now configured to work **without virtual environments** by default. This simplifies the development workflow.

### Poetry Configuration

In `pyproject.toml`:
```toml
[tool.poetry.virtualenvs]
create = false
in-project = false
```

This tells Poetry to install packages directly to the system Python (or container Python in Docker).

## Running Tests

### In Docker (Recommended)

Tests run inside the Docker container which has all dependencies:

```bash
# Unit tests only (fast) - UI tests skipped if Playwright not installed
make test

# Rebuild container to install Playwright
make rebuild

# Then run UI tests
make test-ui

# Or run all tests
make test-all
```

### Locally on Mac (Without Docker)

If you want to run tests locally without Docker:

1. **Install dependencies without venv:**
   ```bash
   poetry config virtualenvs.create false
   poetry install --with dev
   ```

2. **Install Playwright browsers (for UI tests):**
   ```bash
   poetry run playwright install chromium
   ```

3. **Run tests:**
   ```bash
   poetry run pytest -m "not ui"  # Unit tests only
   poetry run pytest -m ui        # UI tests only  
   poetry run pytest              # All tests
   ```

### UI Tests Behavior

- **Without Playwright**: UI test files are automatically skipped (no errors)
- **With Playwright**: All UI tests run normally
- This allows tests to run even before Playwright is set up

## Troubleshooting

### Virtual Environment Still Created

If Poetry still creates a virtual environment:

```bash
# Remove existing venv
rm -rf .venv

# Configure Poetry
poetry config virtualenvs.create false --local

# Reinstall
poetry install --with dev
```

### Tests Can't Find Modules

Make sure you're running tests through Poetry or in Docker:

```bash
# Use poetry run
poetry run pytest

# Or use make commands (Docker)
make test
```

### UI Tests Not Running

If UI tests are skipped but you want to run them:

1. Make sure Playwright is installed:
   ```bash
   # In Docker
   make rebuild
   
   # Locally
   poetry run playwright install chromium
   ```

2. Verify installation:
   ```bash
   # In Docker
   docker compose exec web python -c "import playwright; print('OK')"
   
   # Locally
   poetry run python -c "import playwright; print('OK')"
   ```

### "Module not found" Errors

If you see module import errors:

1. In Docker: Rebuild the container
   ```bash
   make rebuild
   ```

2. Locally: Reinstall dependencies
   ```bash
   poetry install --with dev
   ```
