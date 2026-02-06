"""UI tests for Matching Exercise using Playwright."""

import pytest

# Skip entire module if playwright not available
pytest.importorskip("playwright.sync_api")

from playwright.sync_api import Page, expect  # noqa: E402

from vocabulary.models import Language, Translation, Word  # noqa: E402

pytestmark = pytest.mark.ui


@pytest.fixture(scope="function")
def matching_test_data(db):
    """Create test data for matching exercise UI tests."""
    # Create languages
    english = Language.objects.create(code="en", name="English")
    hungarian = Language.objects.create(code="hu", name="Hungarian")

    # Create English words
    words_en = []
    words_hu = []
    pairs = [
        ("apple", "a fruit", "alma", "egy gyümölcs"),
        ("book", "something to read", "könyv", "olvasni való"),
        ("house", "a building", "ház", "egy épület"),
        ("water", "a liquid", "víz", "egy folyadék"),
        ("sun", "a star", "nap", "egy csillag"),
    ]

    for en_word, en_def, hu_word, hu_def in pairs:
        word_en = Word.objects.create(
            language=english, word=en_word, definition=en_def
        )
        word_hu = Word.objects.create(
            language=hungarian, word=hu_word, definition=hu_def
        )
        words_en.append(word_en)
        words_hu.append(word_hu)
        Translation.objects.create(source_word=word_en, target_word=word_hu)

    return {
        "languages": {"en": english, "hu": hungarian},
        "words_en": words_en,
        "words_hu": words_hu,
    }


@pytest.mark.django_db
def test_matching_page_loads(page: Page, live_server, matching_test_data):
    """Test that the matching exercise page loads successfully."""
    page.goto(f"{live_server.url}/exercises/matching/")
    expect(page).to_have_title("Matching Exercise")
    expect(page.locator("h1")).to_contain_text("Word Matching")


@pytest.mark.django_db
def test_matching_language_selectors(page: Page, live_server, matching_test_data):
    """Test that language selectors are present."""
    page.goto(f"{live_server.url}/exercises/matching/")

    source_select = page.locator("#source_language")
    target_select = page.locator("#target_language")
    count_select = page.locator("#count")

    expect(source_select).to_be_visible()
    expect(target_select).to_be_visible()
    expect(count_select).to_be_visible()


@pytest.mark.django_db
def test_matching_load_exercise(page: Page, live_server, matching_test_data):
    """Test loading a matching exercise."""
    page.goto(f"{live_server.url}/exercises/matching/")

    # Select languages
    page.select_option("#source_language", "en")
    page.wait_for_timeout(500)

    page.select_option("#target_language", "hu")
    page.wait_for_timeout(500)

    page.select_option("#count", "3")
    page.wait_for_timeout(500)

    # Click load button
    page.click("button.action-primary")
    page.wait_for_load_state("networkidle")

    # Verify match board is visible
    match_board = page.locator("#match-board")
    expect(match_board).to_be_visible()

    # Verify we have 3 words and 3 translations
    word_items = page.locator(".match-word")
    translation_items = page.locator(".match-translation")

    expect(word_items).to_have_count(3)
    expect(translation_items).to_have_count(3)


@pytest.mark.django_db
def test_matching_click_to_select(page: Page, live_server, matching_test_data):
    """Test clicking words and translations to select them."""
    page.goto(
        f"{live_server.url}/exercises/matching/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    # Click first word
    first_word = page.locator(".match-word").first
    first_word.click()

    # Check if it has selected class
    expect(first_word).to_have_class(lambda x: "selected" in x or "active" in x)


@pytest.mark.django_db
def test_matching_flip_languages_button(page: Page, live_server, matching_test_data):
    """Test the flip languages button."""
    page.goto(
        f"{live_server.url}/exercises/matching/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    # Click flip button
    flip_button = page.locator("#match-flip")
    expect(flip_button).to_be_visible()
    flip_button.click()

    page.wait_for_load_state("networkidle")

    # Verify languages are flipped (source should now be hu, target en)
    source_value = page.locator("#source_language").input_value()
    target_value = page.locator("#target_language").input_value()

    assert source_value == "hu"
    assert target_value == "en"


@pytest.mark.django_db
def test_matching_different_word_counts(page: Page, live_server, matching_test_data):
    """Test loading exercises with different word counts."""
    for count in [2, 3, 5]:
        page.goto(
            f"{live_server.url}/exercises/matching/?source_language=en&target_language=hu&count={count}"
        )
        page.wait_for_load_state("networkidle")

        word_items = page.locator(".match-word")
        expect(word_items).to_have_count(count)


@pytest.mark.django_db
def test_matching_instructions_visible(page: Page, live_server, matching_test_data):
    """Test that instructions are visible when exercise is loaded."""
    page.goto(
        f"{live_server.url}/exercises/matching/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    # Look for instructions or feedback section
    instructions = page.locator(".match-instructions, .match-feedback")
    expect(instructions).to_be_visible()


@pytest.mark.django_db
def test_matching_word_columns_present(page: Page, live_server, matching_test_data):
    """Test that both word columns are present."""
    page.goto(
        f"{live_server.url}/exercises/matching/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    columns = page.locator(".match-column")
    expect(columns).to_have_count(2)

    # Check column headers
    expect(page.locator(".match-column h2").first).to_be_visible()
    expect(page.locator(".match-column h2").nth(1)).to_be_visible()
