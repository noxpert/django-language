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

        response = client.get(reverse("random_word"), {"language": "hu"})

        assert response.status_code == 200
        content = response.content.decode()
        # Should show the Hungarian word created above
        assert "könyv" in content

        response = client.get(reverse("random_word"), {"language": "en"})

        assert response.status_code == 200
        content = response.content.decode()
        # Should show the English word created above
        assert "book" in content

    def test_random_word_view_without_words(self, client):
        response = client.get(reverse("random_word"))

        assert response.status_code == 200
        content = response.content.decode()
        # Should show message about selecting language or no words available
        assert "Select a language" in content or "No words" in content.lower()

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
        en_word = Word.objects.create(
            language=english,
            word="water",
        )

        Translation.objects.create(source_word=hu_word, target_word=en_word)
        Translation.objects.create(source_word=de_word, target_word=en_word)

        response = client.get(reverse("random_word"), {"language": "hu"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "víz" in content

    def test_language_selector_only_shows_languages_with_words(self, client):
        """Test that language selector only shows languages that have words."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        Language.objects.create(code="en", name="English")
        Language.objects.create(code="de", name="German")

        # Only create a word in Hungarian
        Word.objects.create(
            language=hungarian,
            word="alma",
            definition="A fruit",
        )

        response = client.get(reverse("random_word"))
        content = response.content.decode()

        # Hungarian should appear (has words)
        assert "Hungarian" in content

        # English and German should NOT appear (no words)
        # Check that they"re not in select options
        assert "<option value='en'" not in content or "English" not in content
        assert "<option value='de'" not in content or "German" not in content

    def test_random_word_with_definition(self, client):
        """Test that definition is displayed when present."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")

        Word.objects.create(
            language=hungarian,
            word="alma",
            definition="Egy gyümölcs, amely fán terem",
        )

        response = client.get(reverse("random_word"), {"language": "hu"})
        content = response.content.decode()

        assert "alma" in content
        assert "gyümölcs" in content  # Part of definition

    def test_random_word_without_translation(self, client):
        """Test displaying word that has no translations."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")

        Word.objects.create(
            language=hungarian,
            word="különleges",
            definition="Egyedi vagy ritka",
        )

        response = client.get(reverse("random_word"), {"language": "hu"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "különleges" in content
        # Should show "No translation" or similar
        assert "No translation" in content or "translation" in content.lower()

    def test_random_word_empty_language_parameter(self, client):
        """Test view when language parameter is empty."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        Word.objects.create(language=hungarian, word="test")

        response = client.get(reverse("random_word"), {"language": ""})

        assert response.status_code == 200
        # Should not crash, should handle empty language gracefully

    def test_random_word_invalid_language(self, client):
        """Test view with non-existent language code."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        Word.objects.create(language=hungarian, word="test")

        response = client.get(reverse("random_word"), {"language": "xx"})

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

        response = client.get(reverse("random_word"), {"language": "hu"})
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

        response = client.get(reverse("random_word"), {"language": "hu"})

        assert response.status_code == 200
        content = response.content.decode()
        # Should show Hungarian word
        assert "ház" in content
        # Should show English translation (since view gets English translation)
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
        response = client.get(reverse("random_word"), {"language": "hu"})
        assert response.status_code == 200
        content = response.content.decode()
        assert "víz" in content

        # Test English view
        response = client.get(reverse("random_word"), {"language": "en"})
        assert response.status_code == 200
        content = response.content.decode()
        assert "water" in content

    def test_get_translation_returns_none(self, client):
        """Test word without English translation shows "No translation"."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        german = Language.objects.create(code="de", name="German")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        de_word = Word.objects.create(language=german, word="Apfel")

        # Only create Hungarian to German translation (no English)
        Translation.objects.create(source_word=hu_word, target_word=de_word)

        response = client.get(reverse("random_word"), {"language": "hu"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "alma" in content
        assert "No translation" in content


@pytest.mark.django_db
class TestLanguageFiltering:
    """Test that languages are filtered correctly."""

    def test_only_languages_with_words_in_selector(self, client):
        """Test that empty languages don"t appear in the selector."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        Language.objects.create(code="de", name="German")

        # Create words only in Hungarian and English
        Word.objects.create(language=hungarian, word="alma")
        Word.objects.create(language=english, word="apple")

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

        # Initially, no words
        response = client.get(reverse("random_word"))
        languages = list(response.context["languages"])
        assert len(languages) == 0

        # Add a word
        Word.objects.create(language=hungarian, word="alma")

        # Now Hungarian should appear
        response = client.get(reverse("random_word"))
        languages = list(response.context["languages"])
        assert len(languages) == 1
        assert languages[0].code == "hu"

    def test_multiple_languages_with_words(self, client):
        """Test multiple languages all appear when they have words."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        german = Language.objects.create(code="de", name="German")

        Word.objects.create(language=hungarian, word="alma")
        Word.objects.create(language=english, word="apple")
        Word.objects.create(language=german, word="Apfel")

        response = client.get(reverse("random_word"))
        languages = list(response.context["languages"])

        assert len(languages) == 3
        language_codes = [lang.code for lang in languages]
        assert set(language_codes) == {"hu", "en", "de"}
