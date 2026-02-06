# Playwright UI Tests Setup Summary

## Changes Made

### 1. Dependencies Added
- **pyproject.toml**: Added `pytest-playwright` and `playwright` to dev dependencies
- **Dockerfile**: Added Playwright system dependencies and browser installation

### 2. Test Configuration
- **pytest.ini**: Added `ui` marker for Playwright tests
- **conftest.py**: Created Playwright configuration with `live_server` and `page` fixtures

### 3. UI Test Files Created
- **wod/test_ui.py**: Word of the Day UI tests (11 tests)
  - Page loading and basic UI elements
  - Language selection and word display
  - Error messages for invalid states
  - Flag images and data accuracy
  
- **exercises/test_ui_matching.py**: Matching exercise UI tests (10 tests)
  - Page loading and form controls
  - Exercise loading with different configurations
  - Word/translation display and interaction
  - Language flipping functionality
  
- **exercises/test_ui_spelling.py**: Spelling exercise UI tests (10 tests)
  - Page loading and form controls
  - Exercise loading and word display
  - Input field interaction
  - Submit/check functionality

### 4. Makefile Updates
- **make test**: Now excludes UI tests (runs unit tests only)
- **make test-v**: Verbose unit tests only
- **make test-cov**: Coverage report for unit tests only
- **make test-ui**: NEW - Runs only UI tests with Playwright
- **make test-all**: NEW - Runs all tests including UI tests

### 5. CI/CD Updates
- **.github/workflows/ci.yml**: 
  - Added Playwright browser installation step
  - Separated unit tests and UI tests into separate steps
  - Both must pass for CI to succeed

### 6. Documentation Updates
- **README.md**: 
  - Updated Testing & Quality section with new commands
  - Added comprehensive Testing section with examples
  - Explained UI testing setup and usage
  
- **copilot_instructions_updated.md**:
  - Updated Development Workflow section
  - Updated Testing section with new commands
  - Added detailed UI Testing with Playwright section

## How to Use

### Running Tests Locally (Docker)
```bash
# Unit tests only (fast)
make test

# UI tests only (with browser)
make test-ui

# All tests
make test-all

# With coverage report
make test-cov
```

### Running Tests in CI
Tests run automatically on every push and pull request:
1. Unit tests run first
2. UI tests run after
3. Both must pass

### First Time Setup
If you're rebuilding the Docker container:
```bash
make rebuild
```

Playwright browsers will be installed automatically during the Docker build.

### Local Development (without Docker)
```bash
# Install dependencies
poetry install --with dev

# Install Playwright browsers
poetry run playwright install chromium

# Run tests
poetry run pytest -m "not ui"  # Unit tests only
poetry run pytest -m ui        # UI tests only
poetry run pytest              # All tests
```

## Test Markers

All UI tests are marked with `@pytest.mark.ui`:
- Allows selective test execution
- Keeps unit tests fast for rapid iteration
- Enables comprehensive UI coverage when needed

## Test Coverage

### Word of the Day (wod/test_ui.py)
- ✓ Page loads successfully
- ✓ Language selectors visible
- ✓ Word loading with language selection
- ✓ Same language error message
- ✓ No translation available message
- ✓ Flag images display
- ✓ Correct word data display

### Matching Exercise (exercises/test_ui_matching.py)
- ✓ Page loads successfully
- ✓ Language selectors present
- ✓ Exercise loading
- ✓ Click to select words
- ✓ Flip languages button
- ✓ Different word counts
- ✓ Instructions visible
- ✓ Word columns present

### Spelling Exercise (exercises/test_ui_spelling.py)
- ✓ Page loads successfully
- ✓ Language selectors present
- ✓ Exercise loading
- ✓ Input fields present
- ✓ Word display
- ✓ Type answer functionality
- ✓ Check button present
- ✓ Different word counts
- ✓ Flip languages button
- ✓ Instructions visible

## Notes

- UI tests use Chromium browser by default
- Tests run in headless mode in CI
- Tests can run headed locally with `--headed` flag
- Live server starts automatically for each test
- Database is reset between tests
- Tests are isolated and can run in any order
