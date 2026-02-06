"""Playwright UI tests for Spelling Exercise page."""

import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
class TestSpellingExerciseUI:
    """UI tests for the Spelling Exercise page."""

    def test_page_loads(self, authenticated_page: Page, live_server):
        """Test that the spelling exercise page loads successfully."""
        authenticated_page.goto(f"{live_server.url}/exercises/spelling/")
        expect(authenticated_page).to_have_title("Spelling Exercise")

    def test_navigation_visible(self, authenticated_page: Page, live_server):
        """Test that the navigation bar is visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/spelling/")
        nav = authenticated_page.locator(".site-nav")
        expect(nav).to_be_visible()

    def test_spelling_link_is_active(self, authenticated_page: Page, live_server):
        """Test that spelling link is marked as active on the spelling page."""
        authenticated_page.goto(f"{live_server.url}/exercises/spelling/")
        spelling_link = authenticated_page.get_by_role("link", name="Spelling")
        expect(spelling_link).to_have_class(re.compile(r"is-active"))

    def test_page_header_visible(self, authenticated_page: Page, live_server):
        """Test that the page header is visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/spelling/")
        header = authenticated_page.locator(".spelling-header")
        expect(header).to_be_visible()
        expect(authenticated_page.locator("h1")).to_contain_text("Spelling Exercise")

    def test_language_selectors_visible(self, authenticated_page: Page, live_server):
        """Test that language selection dropdowns are visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/spelling/")
        source_select = authenticated_page.locator("#source_language")
        target_select = authenticated_page.locator("#target_language")
        expect(source_select).to_be_visible()
        expect(target_select).to_be_visible()

    def test_load_word_button_visible(self, authenticated_page: Page, live_server):
        """Test that the Load word button is visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/spelling/")
        load_button = authenticated_page.get_by_role("button", name="Load word")
        expect(load_button).to_be_visible()

    def test_navigate_to_wod(self, authenticated_page: Page, live_server):
        """Test navigation from spelling to WoD page."""
        authenticated_page.goto(f"{live_server.url}/exercises/spelling/")
        authenticated_page.get_by_role("link", name="Word of the Day").click()
        expect(authenticated_page).to_have_title("Word of the Day")

    def test_navigate_to_matching(self, authenticated_page: Page, live_server):
        """Test navigation from spelling to matching page."""
        authenticated_page.goto(f"{live_server.url}/exercises/spelling/")
        authenticated_page.get_by_role("link", name="Word Matching").click()
        expect(authenticated_page).to_have_title("Matching Exercise")
