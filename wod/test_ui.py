"""Playwright UI tests for Word of the Day page."""

import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
class TestWordOfDayUI:
    """UI tests for the Word of the Day page."""

    def test_page_loads(self, authenticated_page: Page, live_server):
        """Test that the WoD page loads successfully."""
        authenticated_page.goto(f"{live_server.url}/")
        expect(authenticated_page).to_have_title("Word of the Day")

    def test_navigation_visible(self, authenticated_page: Page, live_server):
        """Test that the navigation bar is visible."""
        authenticated_page.goto(f"{live_server.url}/")
        nav = authenticated_page.locator(".site-nav")
        expect(nav).to_be_visible()

    def test_nav_links_present(self, authenticated_page: Page, live_server):
        """Test that all navigation links are present."""
        authenticated_page.goto(f"{live_server.url}/")
        expect(
            authenticated_page.get_by_role("link", name="Word of the Day")
        ).to_be_visible()
        expect(
            authenticated_page.get_by_role("link", name="Word Matching")
        ).to_be_visible()
        expect(authenticated_page.get_by_role("link", name="Spelling")).to_be_visible()

    def test_wod_link_is_active(self, authenticated_page: Page, live_server):
        """Test that WoD link is marked as active on the WoD page."""
        authenticated_page.goto(f"{live_server.url}/")
        wod_link = authenticated_page.get_by_role("link", name="Word of the Day")
        expect(wod_link).to_have_class(re.compile(r"is-active"))

    def test_language_selectors_visible(self, authenticated_page: Page, live_server):
        """Test that language selection dropdowns are visible."""
        authenticated_page.goto(f"{live_server.url}/")
        source_select = authenticated_page.locator("#source_language")
        target_select = authenticated_page.locator("#target_language")
        expect(source_select).to_be_visible()
        expect(target_select).to_be_visible()

    def test_logout_link_present(self, authenticated_page: Page, live_server):
        """Test that the logout link is visible."""
        authenticated_page.goto(f"{live_server.url}/")
        logout_link = authenticated_page.get_by_role("link", name="Log out")
        expect(logout_link).to_be_visible()

    def test_user_display_in_nav(self, authenticated_page: Page, live_server):
        """Test that the logged-in user is displayed in nav."""
        authenticated_page.goto(f"{live_server.url}/")
        # User display should show either name or email
        user_display = authenticated_page.locator(".site-nav-user")
        expect(user_display).to_be_visible()
