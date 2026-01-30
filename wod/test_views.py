import re

import pytest
from django.urls import reverse

from vocabulary.models import Language, Translation, Word


@pytest.mark.django_db
class TestRandomWordView:
    def test_random_word_view_with_words(self, client):
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(
            language=hungarian,
            word="könyv",
            definition="A written work",
        )
        en_word = Word.objects.create(
            language=english,
            word="book",
            definition="A written or printed work",
        )

        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(
            reverse("random_word"),
            {"source_language": "hu", "target_language": "en"},
        )

        assert response.status_code == 200
        content = response.content.decode()
        # Should show the Hungarian word created above
        assert "könyv" in content
        assert "book" in content

        response = client.get(
            reverse("random_word"),
            {"source_language": "en", "target_language": "hu"},
        )

        assert response.status_code == 200
        content = response.content.decode()
        # Should show the English word created above
        assert "book" in content

    def test_random_word_view_without_words(self, client):
        response = client.get(reverse("random_word"))

        assert response.status_code == 200
        content = response.content.decode()
        # Should show message about selecting language or no words available
        assert "Choose languages" in content or "No words" in content

    def test_random_word_same_language_message(self, client):
        english = Language.objects.create(code="en", name="English")
        Word.objects.create(language=english, word="book")

        response = client.get(
            reverse("random_word"),
            {"source_language": "en", "target_language": "en"},
        )

        assert response.status_code == 200
        assert response.context["same_language"] is True
        assert response.context["word"] is None
        content = response.content.decode()
        assert "Please choose two different languages to start." in content

    def test_random_word_defaults_to_first_pair(self, client):
        english = Language.objects.create(code="en", name="English")
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        hu_word = Word.objects.create(language=hungarian, word="toll")
        en_word = Word.objects.create(language=english, word="pen")
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(reverse("random_word"))

        assert response.status_code == 200
        assert response.context["source_language"] == english.code
        assert response.context["target_language"] == hungarian.code
        content = response.content.decode()
        assert "pen" in content or "toll" in content

    def test_random_word_view_language_filter(self, client):
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        german = Language.objects.create(code="de", name="German")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(
            language=hungarian,
            word="víz",
            definition="H2O",
        )
        de_word = Word.objects.create(
            language=german,
            word="Wasser",
            definition="H2O",
        )
        hu_alt = Word.objects.create(
            language=hungarian,
            word="folyó",
            definition="River",
        )
        en_word = Word.objects.create(
            language=english,
            word="water",
        )

        Translation.objects.create(source_word=hu_word, target_word=en_word)
        Translation.objects.create(source_word=hu_alt, target_word=de_word)
        Translation.objects.create(source_word=de_word, target_word=en_word)

        response = client.get(
            reverse("random_word"),
            {"source_language": "hu", "target_language": "en"},
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "víz" in content
        assert "folyó" not in content

    def test_random_word_avoids_repeat(self, client):
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        hu_word_one = Word.objects.create(language=hungarian, word="alma")
        en_word_one = Word.objects.create(language=english, word="apple")
        hu_word_two = Word.objects.create(language=hungarian, word="körte")
        en_word_two = Word.objects.create(language=english, word="pear")
        Translation.objects.create(source_word=hu_word_one, target_word=en_word_one)
        Translation.objects.create(source_word=hu_word_two, target_word=en_word_two)

        session = client.session
        session["wod_last_word_id"] = hu_word_one.id
        session.save()

        response = client.get(
            reverse("random_word"),
            {"source_language": "hu", "target_language": "en"},
        )

        assert response.status_code == 200
        assert response.context["word"].id != hu_word_one.id

    def test_language_selector_only_shows_languages_with_words(self, client):
        """Test that language selector only shows languages that have translations."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        Language.objects.create(code="de", name="German")

        # Only create a word in Hungarian and a translation to English
        hu_word = Word.objects.create(
            language=hungarian,
            word="alma",
            definition="A fruit",
        )
        en_word = Word.objects.create(
            language=english,
            word="apple",
            definition="A fruit",
        )
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(reverse("random_word"))
        languages = list(response.context["languages"])
        language_codes = {lang.code for lang in languages}

        # Hungarian and English should appear (translation pair)
        assert "hu" in language_codes
        assert "en" in language_codes

        # German should NOT appear (no words or translations)
        assert "de" not in language_codes

    def test_random_word_with_definition(self, client):
        """Test that definition is displayed when present."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(
            language=hungarian,
            word="alma",
            definition="Egy gyümölcs, amely fán terem",
        )
        en_word = Word.objects.create(
            language=english,
            word="apple",
            definition="A round fruit",
        )
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(
            reverse("random_word"),
            {"source_language": "hu", "target_language": "en"},
        )
        content = response.content.decode()

        assert "alma" in content
        assert "round fruit" in content

    def test_random_word_without_translation(self, client):
        """Test empty state when no translation exists for the selected pairing."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        german = Language.objects.create(code="de", name="German")
        Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(
            language=hungarian,
            word="különleges",
            definition="Egyedi vagy ritka",
        )
        de_word = Word.objects.create(language=german, word="besondere")
        Translation.objects.create(source_word=hu_word, target_word=de_word)

        response = client.get(
            reverse("random_word"),
            {"source_language": "hu", "target_language": "en"},
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "különleges" not in content
        assert "No words are available" in content

    def test_random_word_empty_language_parameter(self, client):
        """Test view when language parameter is empty."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        hu_word = Word.objects.create(language=hungarian, word="test")
        en_word = Word.objects.create(language=english, word="test-en")
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(reverse("random_word"), {"source_language": ""})

        assert response.status_code == 200
        # Should not crash, should handle empty language gracefully

    def test_navigation_active_on_random_word(self, client):
        response = client.get(reverse("random_word"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "Word Matching" in content

        active_pattern = re.compile(
            rf'class="site-nav-link is-active"[^>]*href="{re.escape(reverse("random_word"))}"'
        )
        assert active_pattern.search(content)

    def test_random_word_invalid_language(self, client):
        """Test view with non-existent language code."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        hu_word = Word.objects.create(language=hungarian, word="test")
        en_word = Word.objects.create(language=english, word="test-en")
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(
            reverse("random_word"),
            {"source_language": "xx", "target_language": "en"},
        )

        assert response.status_code == 200
        # Should handle gracefully, likely showing no word

    def test_random_word_with_translation(self, client):
        """Test that translation is displayed when available."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(
            language=hungarian,
            word="ház",
            definition="Épület",
        )
        en_word = Word.objects.create(
            language=english,
            word="house",
            definition="A building",
        )

        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(
            reverse("random_word"),
            {"source_language": "hu", "target_language": "en"},
        )
        content = response.content.decode()

        assert "ház" in content
        assert "house" in content  # Translation should be shown


@pytest.mark.django_db
class TestTranslationIntegration:
    """Test how translations work in views."""

    def test_word_with_multiple_translations(self, client):
        """Test word that has multiple translations."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        german = Language.objects.create(code="de", name="German")

        hu_word = Word.objects.create(language=hungarian, word="ház")
        en_word = Word.objects.create(language=english, word="house")
        de_word = Word.objects.create(language=german, word="Haus")

        Translation.objects.create(source_word=hu_word, target_word=en_word)
        Translation.objects.create(source_word=hu_word, target_word=de_word)

        response = client.get(
            reverse("random_word"),
            {"source_language": "hu", "target_language": "en"},
        )

        assert response.status_code == 200
        content = response.content.decode()
        # Should show Hungarian word
        assert "ház" in content
        # Should show English translation (target language)
        assert "house" in content

    def test_bidirectional_translations_display(self, client):
        """Test that bidirectional translations work correctly."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="víz")
        en_word = Word.objects.create(language=english, word="water")

        # Create bidirectional translations
        Translation.objects.create(source_word=hu_word, target_word=en_word)
        Translation.objects.create(source_word=en_word, target_word=hu_word)

        # Test Hungarian view
        response = client.get(
            reverse("random_word"),
            {"source_language": "hu", "target_language": "en"},
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "víz" in content

        # Test English view
        response = client.get(
            reverse("random_word"),
            {"source_language": "en", "target_language": "hu"},
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "water" in content

    def test_get_translation_returns_none(self, client):
        """Test empty state when no translation to the selected target exists."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        german = Language.objects.create(code="de", name="German")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        de_word = Word.objects.create(language=german, word="Apfel")
        Word.objects.create(language=english, word="apple")

        # Only create Hungarian to German translation (no English)
        Translation.objects.create(source_word=hu_word, target_word=de_word)

        response = client.get(
            reverse("random_word"),
            {"source_language": "hu", "target_language": "en"},
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "alma" not in content
        assert "No words are available" in content


@pytest.mark.django_db
class TestLanguageFiltering:
    """Test that languages are filtered correctly."""

    def test_only_languages_with_words_in_selector(self, client):
        """Test that empty languages don"t appear in the selector."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        Language.objects.create(code="de", name="German")

        # Create words in Hungarian and English with translations
        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(reverse("random_word"))

        # Check that the response includes the languages list
        assert "languages" in response.context
        languages = list(response.context["languages"])

        # Should only have Hungarian and English
        language_codes = [lang.code for lang in languages]
        assert "hu" in language_codes
        assert "en" in language_codes
        assert "de" not in language_codes

    def test_language_appears_after_adding_word(self, client):
        """Test that language appears in selector after adding first word."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        # Initially, no words
        response = client.get(reverse("random_word"))
        languages = list(response.context["languages"])
        assert len(languages) == 0

        # Add a word and translation
        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        # Now Hungarian and English should appear
        response = client.get(reverse("random_word"))
        languages = list(response.context["languages"])
        language_codes = {lang.code for lang in languages}
        assert language_codes == {"hu", "en"}

    def test_multiple_languages_with_words(self, client):
        """Test multiple languages all appear when they have words."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        german = Language.objects.create(code="de", name="German")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")
        de_word = Word.objects.create(language=german, word="Apfel")
        Translation.objects.create(source_word=hu_word, target_word=en_word)
        Translation.objects.create(source_word=de_word, target_word=en_word)

        response = client.get(reverse("random_word"))
        languages = list(response.context["languages"])

        assert len(languages) == 3
        language_codes = [lang.code for lang in languages]
        assert set(language_codes) == {"hu", "en", "de"}
