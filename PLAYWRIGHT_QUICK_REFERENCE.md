# Playwright UI Tests - Quick Reference

## Running Tests

### Using Makefile (Recommended)
```bash
make test           # Unit tests only (fast, excludes UI)
make test-ui        # UI tests only (Playwright)
make test-all       # All tests (unit + UI)
make test-cov       # Coverage report (unit tests)
```

### Using Docker Directly
```bash
docker compose exec web pytest -m "not ui"    # Unit tests
docker compose exec web pytest -m ui          # UI tests
docker compose exec web pytest                # All tests
```

### Using Poetry (Local)
```bash
poetry run pytest -m "not ui"    # Unit tests
poetry run pytest -m ui          # UI tests
poetry run pytest                # All tests
```

## Test Files

| File | Tests | Description |
|------|-------|-------------|
| `wod/test_ui.py` | 11 | Word of the Day page tests |
| `exercises/test_ui_matching.py` | 10 | Matching exercise tests |
| `exercises/test_ui_spelling.py` | 10 | Spelling exercise tests |

## Common Commands

```bash
# Run specific test file
docker compose exec web pytest wod/test_ui.py

# Run specific test
docker compose exec web pytest wod/test_ui.py::test_wod_page_loads

# Run with verbose output
docker compose exec web pytest -m ui -v

# Run UI tests in headed mode (show browser)
docker compose exec web pytest -m ui --headed

# Run and stop on first failure
docker compose exec web pytest -m ui -x
```

## First Time Setup

### With Docker (Automatic)
```bash
make rebuild
# Playwright browsers install automatically
```

### Local Development
```bash
poetry install --with dev
poetry run playwright install chromium
```

## Debugging UI Tests

### See Browser Window
```bash
docker compose exec web pytest -m ui --headed
```

### Slow Down Tests
```bash
docker compose exec web pytest -m ui --slowmo 1000
```

### Screenshot on Failure
Automatically captured in `test-results/` directory

### Video Recording
Add to pytest command:
```bash
docker compose exec web pytest -m ui --video on
```

## Writing New UI Tests

### Template
```python
import pytest
from playwright.sync_api import Page, expect
from vocabulary.models import Language, Word, Translation

pytestmark = pytest.mark.ui

@pytest.fixture(scope="function")
def test_data(db):
    # Create test data
    pass

@pytest.mark.django_db
def test_something(page: Page, live_server, test_data):
    page.goto(f"{live_server.url}/path")
    expect(page.locator("h1")).to_contain_text("Expected")
```

### Best Practices
1. Always mark with `@pytest.mark.ui`
2. Use `@pytest.mark.django_db` for database access
3. Create fixtures for test data
4. Use `live_server` fixture for URLs
5. Use `page` fixture for browser interaction
6. Use `expect()` for assertions
7. Wait for page loads with `page.wait_for_load_state("networkidle")`

## Playwright Selectors

```python
# By ID
page.locator("#element-id")

# By class
page.locator(".class-name")

# By text
page.locator("text=Click me")

# By role
page.locator("role=button")

# CSS selector
page.locator("button.primary")

# First/last/nth
page.locator(".item").first
page.locator(".item").last
page.locator(".item").nth(2)
```

## Common Assertions

```python
# Visibility
expect(element).to_be_visible()
expect(element).to_be_hidden()

# Text content
expect(element).to_contain_text("Hello")
expect(element).to_have_text("Exact text")

# Attributes
expect(element).to_have_attribute("href", "/path")
expect(element).to_have_class("active")

# Count
expect(elements).to_have_count(5)

# Page
expect(page).to_have_title("Page Title")
expect(page).to_have_url("http://example.com/path")
```

## Troubleshooting

### Tests fail with "browser not found"
```bash
# In Docker, rebuild:
make rebuild

# Locally:
poetry run playwright install chromium
```

### Tests timeout
- Increase timeout: `page.set_default_timeout(10000)`  # 10 seconds
- Check if server is running
- Check for JavaScript errors in console

### Can't see what's happening
```bash
# Run in headed mode
make test-ui --headed  # If Makefile supports it
# Or:
docker compose exec web pytest -m ui --headed --slowmo 500
```

### Tests pass locally but fail in CI
- Check screen resolution differences
- Check if data is properly set up
- Check for timing issues (add explicit waits)

## CI/CD

Tests run automatically on:
- Every push to any branch
- Every pull request

Order:
1. Unit tests run first (fast feedback)
2. UI tests run after (comprehensive)
3. Both must pass for build to succeed

View results in GitHub Actions tab.
