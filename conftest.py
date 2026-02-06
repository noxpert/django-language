"""Pytest configuration for Playwright UI tests."""

import pytest

# Check if Playwright is available
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "ui: marks tests as UI tests (playwright)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip UI tests if Playwright is not available."""
    if PLAYWRIGHT_AVAILABLE:
        return

    skip_ui = pytest.mark.skip(reason="Playwright not installed")
    for item in items:
        if "ui" in item.keywords:
            item.add_marker(skip_ui)


@pytest.fixture(scope="session")
def django_db_setup():
    """Set up test database for Playwright tests."""
    pass


@pytest.fixture(scope="function")
def live_server(request, django_db_setup, django_db_blocker):
    """Start a live Django server for Playwright tests."""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")

    from django.test.testcases import LiveServerThread
    import socket

    # Find an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]

    # Create and start the live server
    server = LiveServerThread("localhost", [port], None)

    with django_db_blocker.unblock():
        server.start()
        server.is_ready.wait()

        class ServerInfo:
            url = f"http://localhost:{port}"

        yield ServerInfo()

        server.terminate()
        server.join()


@pytest.fixture(scope="function")
def page(browser):
    """Create a new page for each test."""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")

    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
