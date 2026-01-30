import json
import re

from django.test import TestCase
from django.urls import reverse

from vocabulary.models import Language, Translation, Word


class MatchingExerciseViewTests(TestCase):
    def setUp(self):
        self.language = Language.objects.create(code="en", name="English")
        self.translation_language = Language.objects.create(code="hu", name="Hungarian")
        self.translation_map = {}
        for index in range(6):
            source_word = Word.objects.create(
                language=self.language,
                word=f"word{index}",
                definition=f"definition{index}",
            )
            target_word = Word.objects.create(
                language=self.translation_language,
                word=f"translation{index}",
                definition=f"definition{index}",
            )
            Translation.objects.create(source_word=source_word, target_word=target_word)
            self.translation_map[source_word.id] = target_word

    def test_exercise_view_without_language(self):
        response = self.client.get(reverse("exercises:matching"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["source_language"], self.language.code)
        self.assertEqual(
            response.context["target_language"], self.translation_language.code
        )
        self.assertEqual(response.context["count"], 5)
        self.assertEqual(len(response.context["words"]), 5)

    def test_exercise_view_with_language(self):
        response = self.client.get(
            reverse("exercises:matching"),
            {
                "source_language": self.language.code,
                "target_language": self.translation_language.code,
                "count": 3,
            },
        )
        self.assertEqual(response.status_code, 200)
        words = response.context["words"]
        translations = response.context["translations"]
        self.assertEqual(len(words), 3)
        expected_translations = [self.translation_map[word.id] for word in words]
        self.assertCountEqual(translations, expected_translations)

    def test_count_is_clamped(self):
        response = self.client.get(
            reverse("exercises:matching"),
            {
                "source_language": self.language.code,
                "target_language": self.translation_language.code,
                "count": 1,
            },
        )
        self.assertEqual(response.context["count"], 2)

        response = self.client.get(
            reverse("exercises:matching"),
            {
                "source_language": self.language.code,
                "target_language": self.translation_language.code,
                "count": 12,
            },
        )
        self.assertEqual(response.context["count"], 10)

    def test_exercise_view_filters_by_target_language(self):
        german = Language.objects.create(code="de", name="German")
        non_matching_word = Word.objects.create(
            language=self.language,
            word="extra",
            definition="definition",
        )
        german_word = Word.objects.create(
            language=german,
            word="extra-de",
            definition="definition",
        )
        Translation.objects.create(
            source_word=non_matching_word, target_word=german_word
        )

        response = self.client.get(
            reverse("exercises:matching"),
            {
                "source_language": self.language.code,
                "target_language": self.translation_language.code,
                "count": 10,
            },
        )
        words = response.context["words"]
        self.assertNotIn(non_matching_word, words)

    def test_exercise_view_same_language_message(self):
        response = self.client.get(
            reverse("exercises:matching"),
            {
                "source_language": self.language.code,
                "target_language": self.language.code,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["same_language"])
        self.assertEqual(len(response.context["words"]), 0)
        content = response.content.decode()
        self.assertIn(
            "Please choose two different languages to start the exercise.",
            content,
        )

    def test_navigation_active_on_matching(self):
        response = self.client.get(reverse("exercises:matching"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Word Matching", content)

        active_pattern = re.compile(
            rf'class="site-nav-link is-active"[^>]*href="{re.escape(reverse("exercises:matching"))}"'
        )
        self.assertRegex(content, active_pattern)


class MatchingCheckViewTests(TestCase):
    def setUp(self):
        self.language = Language.objects.create(code="en", name="English")
        self.translation_language = Language.objects.create(code="hu", name="Hungarian")
        self.words = []
        self.translation_map = {}
        for index in range(4):
            source_word = Word.objects.create(
                language=self.language,
                word=f"alpha{index}",
                definition=f"definition{index}",
            )
            target_word = Word.objects.create(
                language=self.translation_language,
                word=f"beta{index}",
                definition=f"definition{index}",
            )
            Translation.objects.create(source_word=source_word, target_word=target_word)
            self.words.append(source_word)
            self.translation_map[source_word.id] = target_word

    def test_check_matches_all_correct(self):
        matches = {
            str(word.id): self.translation_map[word.id].id for word in self.words
        }
        response = self.client.post(
            reverse("exercises:matching_check"),
            data=json.dumps({"matches": matches}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["score"], len(self.words))

    def test_check_matches_all_incorrect(self):
        wrong_translation = Word.objects.create(
            language=self.translation_language,
            word="wrong",
            definition="definition",
        )
        matches = {str(word.id): wrong_translation.id for word in self.words}
        response = self.client.post(
            reverse("exercises:matching_check"),
            data=json.dumps({"matches": matches}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["score"], 0)
        self.assertEqual(data["total"], len(self.words))

    def test_check_matches_empty(self):
        response = self.client.post(
            reverse("exercises:matching_check"),
            data=json.dumps({"matches": {}}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total"], 0)
