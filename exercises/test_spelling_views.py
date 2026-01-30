import json
import re

import pytest
from django.urls import reverse

from vocabulary.models import Language, Translation, Word


@pytest.mark.django_db
class TestSpellingExerciseView:
    def test_spelling_exercise_loads_word(self, client):
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        hu_word = Word.objects.create(language=hungarian, word="könyv")
        en_word = Word.objects.create(language=english, word="book")
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(
            reverse("exercises:spelling"),
            {"source_language": "hu", "target_language": "en"},
        )

        assert response.status_code == 200
        assert response.context["word"] == hu_word
        assert response.context["translation_word"] == en_word
        content = response.content.decode()
        assert "könyv" in content
        assert f'data-word-id="{hu_word.id}"' in content
        assert f'data-translation-id="{en_word.id}"' in content

    def test_spelling_exercise_defaults_to_first_pair(self, client):
        english = Language.objects.create(code="en", name="English")
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        hu_word = Word.objects.create(language=hungarian, word="toll")
        en_word = Word.objects.create(language=english, word="pen")
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        response = client.get(reverse("exercises:spelling"))

        assert response.status_code == 200
        assert response.context["source_language"] == english.code
        assert response.context["target_language"] == hungarian.code
        assert response.context["word"] == en_word

    def test_spelling_exercise_empty_pairing(self, client):
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        german = Language.objects.create(code="de", name="German")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="különleges")
        de_word = Word.objects.create(language=german, word="besondere")
        Translation.objects.create(source_word=hu_word, target_word=de_word)
        Word.objects.create(language=english, word="special")

        response = client.get(
            reverse("exercises:spelling"),
            {"source_language": "hu", "target_language": "en"},
        )

        assert response.status_code == 200
        assert response.context["word"] is None
        content = response.content.decode()
        assert "No words are available for this pairing yet." in content

    def test_spelling_exercise_avoids_repeat(self, client):
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        hu_word_one = Word.objects.create(language=hungarian, word="alma")
        en_word_one = Word.objects.create(language=english, word="apple")
        hu_word_two = Word.objects.create(language=hungarian, word="korte")
        en_word_two = Word.objects.create(language=english, word="pear")
        Translation.objects.create(source_word=hu_word_one, target_word=en_word_one)
        Translation.objects.create(source_word=hu_word_two, target_word=en_word_two)

        session = client.session
        session["spelling_last_word_id"] = hu_word_one.id
        session.save()

        response = client.get(
            reverse("exercises:spelling"),
            {"source_language": "hu", "target_language": "en"},
        )

        assert response.status_code == 200
        assert response.context["word"].id != hu_word_one.id

    def test_spelling_exercise_same_language_message(self, client):
        english = Language.objects.create(code="en", name="English")
        Word.objects.create(language=english, word="book")

        response = client.get(
            reverse("exercises:spelling"),
            {"source_language": "en", "target_language": "en"},
        )

        assert response.status_code == 200
        assert response.context["same_language"] is True
        assert response.context["word"] is None
        content = response.content.decode()
        assert "Please choose two different languages to start the exercise." in content

    def test_navigation_active_on_spelling(self, client):
        response = client.get(reverse("exercises:spelling"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "Word Matching" in content
        assert "Spelling" in content

        active_pattern = re.compile(
            rf'class="site-nav-link is-active"[^>]*href="{re.escape(reverse("exercises:spelling"))}"'
        )
        assert active_pattern.search(content)

    def test_check_spelling_scores_answer(self, client):
        english = Language.objects.create(code="en", name="English")
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        en_word = Word.objects.create(language=english, word="apple")
        hu_word = Word.objects.create(language=hungarian, word="alma")
        Translation.objects.create(source_word=en_word, target_word=hu_word)

        response = client.post(
            reverse("exercises:spelling_check"),
            data=json.dumps(
                {
                    "word_id": en_word.id,
                    "translation_id": hu_word.id,
                    "answer": "álma",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["score"] == 95
        assert "Almost" in data["message"]

    def test_check_spelling_translation_mismatch(self, client):
        english = Language.objects.create(code="en", name="English")
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        german = Language.objects.create(code="de", name="German")
        en_word = Word.objects.create(language=english, word="apple")
        hu_word = Word.objects.create(language=hungarian, word="alma")
        de_word = Word.objects.create(language=german, word="apfel")
        Translation.objects.create(source_word=en_word, target_word=de_word)

        response = client.post(
            reverse("exercises:spelling_check"),
            data=json.dumps(
                {
                    "word_id": en_word.id,
                    "translation_id": hu_word.id,
                    "answer": "alma",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_check_spelling_reveals_answer_after_three_wrong(self, client):
        english = Language.objects.create(code="en", name="English")
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        en_word = Word.objects.create(language=english, word="apple")
        hu_word = Word.objects.create(language=hungarian, word="alma")
        Translation.objects.create(source_word=en_word, target_word=hu_word)

        for _ in range(2):
            response = client.post(
                reverse("exercises:spelling_check"),
                data=json.dumps(
                    {
                        "word_id": en_word.id,
                        "translation_id": hu_word.id,
                        "answer": "wrong",
                    }
                ),
                content_type="application/json",
            )
            assert response.status_code == 200
            assert response.json()["correct_spelling"] is None

        response = client.post(
            reverse("exercises:spelling_check"),
            data=json.dumps(
                {
                    "word_id": en_word.id,
                    "translation_id": hu_word.id,
                    "answer": "wrong",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["correct_spelling"] == "alma"
