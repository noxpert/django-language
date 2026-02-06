"""UI tests for Word of the Day using Playwright."""

import pytest

# Skip entire module if playwright not available
pytest.importorskip("playwright.sync_api")

from playwright.sync_api import Page, expect  # noqa: E402

from vocabulary.models import Language, Translation, Word  # noqa: E402

pytestmark = pytest.mark.ui


@pytest.fixture(scope="function")
def test_data(db):
    """Create test data for WOD UI tests."""
    # Create languages
    english = Language.objects.create(code="en", name="English")
    hungarian = Language.objects.create(code="hu", name="Hungarian")
    german = Language.objects.create(code="de", name="German")

    # Create English words
    hello_en = Word.objects.create(
        language=english, word="hello", definition="a greeting"
    )
    goodbye_en = Word.objects.create(
        language=english, word="goodbye", definition="a farewell"
    )

    # Create Hungarian words
    hello_hu = Word.objects.create(
        language=hungarian, word="szia", definition="üdvözlés"
    )
    goodbye_hu = Word.objects.create(
        language=hungarian, word="viszlát", definition="búcsú"
    )

    # Create German words
    hello_de = Word.objects.create(
        language=german, word="hallo", definition="eine Begrüßung"
    )

    # Create translations
    Translation.objects.create(source_word=hello_en, target_word=hello_hu)
    Translation.objects.create(source_word=goodbye_en, target_word=goodbye_hu)
    Translation.objects.create(source_word=hello_en, target_word=hello_de)

    return {
        "languages": {"en": english, "hu": hungarian, "de": german},
        "words": {
            "hello_en": hello_en,
            "goodbye_en": goodbye_en,
            "hello_hu": hello_hu,
            "goodbye_hu": goodbye_hu,
            "hello_de": hello_de,
        },
    }


@pytest.mark.django_db
def test_wod_page_loads(page: Page, live_server, test_data):
    """Test that the Word of the Day page loads successfully."""
    page.goto(f"{live_server.url}/")
    expect(page).to_have_title("Word of the Day")
    expect(page.locator("h1")).to_contain_text("Word of the Day")


@pytest.mark.django_db
def test_wod_language_selectors_visible(page: Page, live_server, test_data):
    """Test that language selectors are visible."""
    page.goto(f"{live_server.url}/")

    # Check for language selectors
    source_select = page.locator("#source_language")
    target_select = page.locator("#target_language")

    expect(source_select).to_be_visible()
    expect(target_select).to_be_visible()


@pytest.mark.django_db
def test_wod_select_languages_and_load_word(page: Page, live_server, test_data):
    """Test selecting languages and loading a word."""
    page.goto(f"{live_server.url}/")

    # Select source language (Hungarian)
    page.select_option("#source_language", "hu")

    # Wait for auto-submit and page reload
    page.wait_for_load_state("networkidle")

    # Select target language (English)
    page.select_option("#target_language", "en")

    # Wait for auto-submit and page reload
    page.wait_for_load_state("networkidle")

    # Check that a word is displayed
    word_section = page.locator(".wod-card")
    expect(word_section).to_be_visible()

    # Check that word elements are visible
    expect(page.locator(".wod-word")).to_be_visible()
    expect(page.locator(".wod-translation")).to_be_visible()
    expect(page.locator(".wod-definition")).to_be_visible()


@pytest.mark.django_db
def test_wod_same_language_shows_error(page: Page, live_server, test_data):
    """Test that selecting the same language shows an error message."""
    page.goto(f"{live_server.url}/")

    # Select same language for both
    page.select_option("#source_language", "en")
    page.wait_for_load_state("networkidle")

    page.select_option("#target_language", "en")
    page.wait_for_load_state("networkidle")

    # Check for error message
    empty_section = page.locator(".wod-empty")
    expect(empty_section).to_be_visible()
    expect(empty_section).to_contain_text("Please choose two different languages")


@pytest.mark.django_db
def test_wod_no_translation_available(page: Page, live_server, test_data):
    """Test message when no translation is available."""
    page.goto(f"{live_server.url}/")

    # Select German to Hungarian (no translation available)
    page.select_option("#source_language", "de")
    page.wait_for_load_state("networkidle")

    page.select_option("#target_language", "hu")
    page.wait_for_load_state("networkidle")

    # Check for no words available message
    empty_section = page.locator(".wod-empty")
    expect(empty_section).to_be_visible()
    expect(empty_section).to_contain_text("No words are available")


@pytest.mark.django_db
def test_wod_flag_images_display(page: Page, live_server, test_data):
    """Test that flag images display correctly."""
    page.goto(f"{live_server.url}/?source_language=hu&target_language=en")
    page.wait_for_load_state("networkidle")

    # Check that flag image is present
    flag_image = page.locator(".wod-flag img")
    expect(flag_image).to_be_visible()


@pytest.mark.django_db
def test_wod_displays_correct_word_data(page: Page, live_server, test_data):
    """Test that the page displays correct word and translation data."""
    # Load the page with specific languages
    page.goto(f"{live_server.url}/?source_language=hu&target_language=en")
    page.wait_for_load_state("networkidle")

    # Get the displayed word (could be szia or viszlát)
    word_text = page.locator(".wod-word").inner_text()

    # Verify it's one of our Hungarian words
    assert word_text in ["szia", "viszlát"]

    # Verify translation is displayed
    translation_text = page.locator(".wod-translation").inner_text()
    assert translation_text in ["hello", "goodbye"]

    # Verify definition is displayed
    definition_text = page.locator(".wod-definition").inner_text()
    assert definition_text in ["a greeting", "a farewell"]
