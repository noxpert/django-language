import os

import pytest
from django.contrib.auth import get_user_model

# Allow Django async-unsafe operations in Playwright tests
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def test_user(db):
    """Create a test user for authentication."""
    User = get_user_model()
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Return a Django test client logged in as test_user."""
    client.force_login(test_user)
    return client


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for playwright tests."""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }


@pytest.fixture
def live_server_url(live_server):
    """Return the live server URL for playwright tests."""
    return live_server.url


@pytest.fixture
def authenticated_page(page, live_server, test_user, client):
    """
    Return a playwright page with an authenticated session.
    Uses Django's session cookie to authenticate.
    """
    # Force login via Django test client
    client.force_login(test_user)

    # Get the session cookie from Django test client
    session_cookie = client.cookies.get("sessionid")
    if session_cookie:
        page.context.add_cookies(
            [
                {
                    "name": "sessionid",
                    "value": session_cookie.value,
                    "domain": "localhost",
                    "path": "/",
                }
            ]
        )

    return page
