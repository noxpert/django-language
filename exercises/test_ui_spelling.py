"""UI tests for Spelling Exercise using Playwright."""

import pytest

# Skip entire module if playwright not available
pytest.importorskip("playwright.sync_api")

from playwright.sync_api import Page, expect  # noqa: E402

from vocabulary.models import Language, Translation, Word  # noqa: E402

pytestmark = pytest.mark.ui


@pytest.fixture(scope="function")
def spelling_test_data(db):
    """Create test data for spelling exercise UI tests."""
    # Create languages
    english = Language.objects.create(code="en", name="English")
    hungarian = Language.objects.create(code="hu", name="Hungarian")

    # Create word pairs
    words_en = []
    words_hu = []
    pairs = [
        ("cat", "a pet animal", "macska", "egy háziállat"),
        ("dog", "a loyal pet", "kutya", "hűséges háziállat"),
        ("tree", "a tall plant", "fa", "egy magas növény"),
        ("flower", "a colorful plant", "virág", "színes növény"),
        ("bird", "a flying animal", "madár", "repülő állat"),
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
def test_spelling_page_loads(page: Page, live_server, spelling_test_data):
    """Test that the spelling exercise page loads successfully."""
    page.goto(f"{live_server.url}/exercises/spelling/")
    expect(page).to_have_title("Spelling Exercise")
    expect(page.locator("h1")).to_contain_text("Spelling")


@pytest.mark.django_db
def test_spelling_language_selectors(page: Page, live_server, spelling_test_data):
    """Test that language selectors are present."""
    page.goto(f"{live_server.url}/exercises/spelling/")

    source_select = page.locator("#source_language")
    target_select = page.locator("#target_language")
    count_select = page.locator("#count")

    expect(source_select).to_be_visible()
    expect(target_select).to_be_visible()
    expect(count_select).to_be_visible()


@pytest.mark.django_db
def test_spelling_load_exercise(page: Page, live_server, spelling_test_data):
    """Test loading a spelling exercise."""
    page.goto(f"{live_server.url}/exercises/spelling/")

    # Select languages
    page.select_option("#source_language", "hu")
    page.wait_for_timeout(500)

    page.select_option("#target_language", "en")
    page.wait_for_timeout(500)

    page.select_option("#count", "3")
    page.wait_for_timeout(500)

    # Click load button
    page.click("button.action-primary")
    page.wait_for_load_state("networkidle")

    # Verify spelling board is visible
    spelling_section = page.locator(".spelling-board, .spell-board")
    expect(spelling_section).to_be_visible()


@pytest.mark.django_db
def test_spelling_input_fields_present(page: Page, live_server, spelling_test_data):
    """Test that input fields are present for spelling."""
    page.goto(
        f"{live_server.url}/exercises/spelling/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    # Look for input fields (could be text inputs or textareas)
    inputs = page.locator("input[type='text'], textarea, .spelling-input, .spell-input")
    # Should have at least one input field
    expect(inputs.first).to_be_visible()


@pytest.mark.django_db
def test_spelling_word_display(page: Page, live_server, spelling_test_data):
    """Test that words are displayed for spelling practice."""
    page.goto(
        f"{live_server.url}/exercises/spelling/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    # Look for word items or question items
    word_items = page.locator(
        ".spelling-item, .spell-item, .spelling-word, .spell-question"
    )
    # Should have at least one word to spell
    expect(word_items.first).to_be_visible()


@pytest.mark.django_db
def test_spelling_type_answer(page: Page, live_server, spelling_test_data):
    """Test typing an answer in the spelling field."""
    page.goto(
        f"{live_server.url}/exercises/spelling/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    # Find first input field
    input_field = page.locator(
        "input[type='text'], textarea, .spelling-input, .spell-input"
    ).first

    if input_field.is_visible():
        # Type a test answer
        input_field.fill("test")

        # Verify the value was entered
        assert input_field.input_value() == "test"


@pytest.mark.django_db
def test_spelling_check_button(page: Page, live_server, spelling_test_data):
    """Test that check/submit button is present."""
    page.goto(
        f"{live_server.url}/exercises/spelling/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    # Look for check or submit button
    check_button = page.locator(
        "button:has-text('Check'), button:has-text('Submit'), .action-primary"
    )
    expect(check_button.first).to_be_visible()


@pytest.mark.django_db
def test_spelling_different_word_counts(page: Page, live_server, spelling_test_data):
    """Test loading exercises with different word counts."""
    for count in [2, 3, 5]:
        page.goto(
            f"{live_server.url}/exercises/spelling/?source_language=en&target_language=hu&count={count}"
        )
        page.wait_for_load_state("networkidle")

        # Verify page loaded successfully
        expect(page.locator("h1")).to_contain_text("Spelling")


@pytest.mark.django_db
def test_spelling_flip_languages_button(page: Page, live_server, spelling_test_data):
    """Test the flip languages button if present."""
    page.goto(
        f"{live_server.url}/exercises/spelling/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    # Look for flip button
    flip_button = page.locator("#spell-flip, #spelling-flip, button:has-text('Flip')")

    if flip_button.count() > 0:
        flip_button.first.click()
        page.wait_for_load_state("networkidle")

        # Verify languages are flipped
        source_value = page.locator("#source_language").input_value()
        target_value = page.locator("#target_language").input_value()

        assert source_value == "hu"
        assert target_value == "en"


@pytest.mark.django_db
def test_spelling_instructions_visible(page: Page, live_server, spelling_test_data):
    """Test that instructions or subtitle are visible."""
    page.goto(
        f"{live_server.url}/exercises/spelling/?source_language=en&target_language=hu&count=3"
    )
    page.wait_for_load_state("networkidle")

    # Look for instructions, subtitle, or description
    instructions = page.locator(
        ".spelling-subtitle, .spell-subtitle, .spelling-instructions, p"
    )
    expect(instructions.first).to_be_visible()
