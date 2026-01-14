import pytest
from django.urls import reverse
from wod.models import Language, Word


@pytest.mark.django_db
class TestRandomWordView:
    def test_random_word_view_with_words(self, client):
        language = Language.objects.create(
            code="hu", name="Hungarian", is_native=False
        )
        Word.objects.create(
            language=language,
            word="könyv",
            translation="book",
            definition="A written work",
        )

        response = client.get(reverse("random_word"))

        assert response.status_code == 200
        assert "könyv" in response.content.decode()
        assert "book" in response.content.decode()

    def test_random_word_view_without_words(self, client):
        response = client.get(reverse("random_word"))

        assert response.status_code == 200
        assert "No words available" in response.content.decode()

    def test_random_word_view_language_filter(self, client):
        hungarian = Language.objects.create(
            code="hu", name="Hungarian", is_native=False
        )
        german = Language.objects.create(code="de", name="German", is_native=False)

        Word.objects.create(
            language=hungarian,
            word="víz",
            translation="water",
            definition="H2O",
        )
        Word.objects.create(
            language=german,
            word="Wasser",
            translation="water",
            definition="H2O",
        )

        response = client.get(reverse("random_word"), {"language": "hu"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "víz" in content or "water" in content

    def test_language_selector_only_shows_languages_with_words(self, client):
        hungarian = Language.objects.create(
            code="hu", name="Hungarian", is_native=False
        )
        Language.objects.create(code="en", name="English", is_native=True)

        Word.objects.create(
            language=hungarian,
            word="alma",
            translation="apple",
            definition="A fruit",
        )

        response = client.get(reverse("random_word"))
        content = response.content.decode()

        assert "Hungarian" in content
        assert "English" not in content
