"""Playwright UI tests for Matching Exercise page."""

import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
class TestMatchingExerciseUI:
    """UI tests for the Matching Exercise page."""

    def test_page_loads(self, authenticated_page: Page, live_server):
        """Test that the matching exercise page loads successfully."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        expect(authenticated_page).to_have_title("Matching Exercise")

    def test_navigation_visible(self, authenticated_page: Page, live_server):
        """Test that the navigation bar is visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        nav = authenticated_page.locator(".site-nav")
        expect(nav).to_be_visible()

    def test_matching_link_is_active(self, authenticated_page: Page, live_server):
        """Test that matching link is marked as active on the matching page."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        matching_link = authenticated_page.get_by_role("link", name="Word Matching")
        expect(matching_link).to_have_class(re.compile(r"is-active"))

    def test_page_header_visible(self, authenticated_page: Page, live_server):
        """Test that the page header is visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        header = authenticated_page.locator(".match-header")
        expect(header).to_be_visible()
        expect(authenticated_page.locator("h1")).to_contain_text("Word Matching")

    def test_language_selectors_visible(self, authenticated_page: Page, live_server):
        """Test that language selection dropdowns are visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        source_select = authenticated_page.locator("#source_language")
        target_select = authenticated_page.locator("#target_language")
        expect(source_select).to_be_visible()
        expect(target_select).to_be_visible()

    def test_count_selector_visible(self, authenticated_page: Page, live_server):
        """Test that word count selector is visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        count_select = authenticated_page.locator("#count")
        expect(count_select).to_be_visible()

    def test_load_set_button_visible(self, authenticated_page: Page, live_server):
        """Test that the Load set button is visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        load_button = authenticated_page.get_by_role("button", name="Load set")
        expect(load_button).to_be_visible()

    def test_flip_languages_button_visible(self, authenticated_page: Page, live_server):
        """Test that the Flip languages button is visible."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        flip_button = authenticated_page.get_by_role("button", name="Flip languages")
        expect(flip_button).to_be_visible()

    def test_navigate_to_wod(self, authenticated_page: Page, live_server):
        """Test navigation from matching to WoD page."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        authenticated_page.get_by_role("link", name="Word of the Day").click()
        expect(authenticated_page).to_have_title("Word of the Day")

    def test_navigate_to_spelling(self, authenticated_page: Page, live_server):
        """Test navigation from matching to spelling page."""
        authenticated_page.goto(f"{live_server.url}/exercises/matching/")
        authenticated_page.get_by_role("link", name="Spelling").click()
        expect(authenticated_page).to_have_title("Spelling Exercise")
