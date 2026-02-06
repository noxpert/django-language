# Copilot Instructions

## Project Overview
Django language learning app for English, Hungarian, and German. Learning goals: AI-assisted development, Django/Python/Poetry/Docker mastery, practical application.

## Recent Changes (February 2025)

### Authentication
- **Auth0 integration** implemented via `accounts/views.py`
- Login/callback/logout flows working
- Admin users configured via `AUTH0_ADMIN_EMAILS` environment variable
  - Set `AUTH0_ADMIN_EMAILS=matthewmorgenegg@gmail.com` for admin access
- Users auto-created on first Auth0 login with email/name from userinfo

### UI Testing
- **Playwright** added for end-to-end UI testing
- Tests located in `wod/test_ui.py`, `exercises/test_ui_matching.py`, `exercises/test_ui_spelling.py`
- Use `@pytest.mark.playwright` marker to identify UI tests
- Makefile commands:
  - `make test` - runs unit tests only (excludes playwright)
  - `make test-ui` - runs only playwright UI tests
  - `make test-all` - runs all tests including playwright

### Navigation
- Logged-in user's name displayed in navbar (falls back to email)
- Logout button positioned on the right

## Next Steps / TODO

### From NextSteps.txt
- [ ] Add README documentation
- [ ] Spelling exercises: show alternate spellings and have user pick correct one
- [ ] Create models for exercise tracking:
  - Per word, per exercise stats
  - Total correct/incorrect counts
  - Longest correct/incorrect streaks
  - Current streak
  - Last 10 answers
- [ ] Display stats to users
- [ ] Use stats to weight word selection

### Admin User Options (Comparison)

**Option A: Environment Variable (Current)**
- `AUTH0_ADMIN_EMAILS` env var lists admin emails
- Users granted `is_staff=True` on login if email matches
- Pros: Simple, secure, already implemented
- Cons: Requires restart to update

**Option B: Database Admin Flag**
- Toggle `is_staff` via Django admin
- Pros: No restart needed, audit trail
- Cons: Requires initial bootstrap superuser

**Option C: Auth0 Roles**
- Assign roles in Auth0 dashboard, map to Django
- Pros: Centralized identity management
- Cons: More complex, Auth0-specific

## Tech Stack
- Django 5.2.8, Python 3.14, Poetry 2.1.3
- Docker (python:3.14-slim), SQLite (dev)
- Auth0 for authentication
- Playwright for UI testing

## Testing Commands
```bash
make test          # Unit tests only
make test-ui       # Playwright UI tests only  
make test-all      # All tests including playwright
make test-cov      # Tests with coverage report
```

## Development Notes
- Playwright tests require browser installation: `playwright install`
- UI tests run against live server fixture (Django test server)
- Docker container runs unit tests; UI tests run locally or in CI with browser setup
