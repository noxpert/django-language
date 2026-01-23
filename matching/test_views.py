import json

from django.test import TestCase
from django.urls import reverse

from vocabulary.models import Language, Word


class MatchingExerciseViewTests(TestCase):
    def setUp(self):
        self.language = Language.objects.create(code="en", name="English", is_native=True)
        for index in range(6):
            Word.objects.create(
                language=self.language,
                word=f"word{index}",
                translation=f"translation{index}",
                definition=f"definition{index}",
            )

    def test_exercise_view_without_language(self):
        response = self.client.get(reverse("matching:exercise"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a language")

    def test_exercise_view_with_language(self):
        response = self.client.get(
            reverse("matching:exercise"),
            {"language": self.language.code, "count": 3},
        )
        self.assertEqual(response.status_code, 200)
        words = response.context["words"]
        translations = response.context["translations"]
        self.assertEqual(len(words), 3)
        self.assertCountEqual(
            translations, [word.translation for word in words]
        )

    def test_count_is_clamped(self):
        response = self.client.get(
            reverse("matching:exercise"),
            {"language": self.language.code, "count": 1},
        )
        self.assertEqual(response.context["count"], 2)

        response = self.client.get(
            reverse("matching:exercise"),
            {"language": self.language.code, "count": 12},
        )
        self.assertEqual(response.context["count"], 10)


class MatchingCheckViewTests(TestCase):
    def setUp(self):
        self.language = Language.objects.create(code="en", name="English", is_native=True)
        self.words = []
        for index in range(4):
            self.words.append(
                Word.objects.create(
                    language=self.language,
                    word=f"alpha{index}",
                    translation=f"beta{index}",
                    definition=f"definition{index}",
                )
            )

    def test_check_matches_all_correct(self):
        matches = {str(word.id): word.translation for word in self.words}
        response = self.client.post(
            reverse("matching:check"),
            data=json.dumps({"matches": matches}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["score"], len(self.words))

    def test_check_matches_all_incorrect(self):
        matches = {str(word.id): "wrong" for word in self.words}
        response = self.client.post(
            reverse("matching:check"),
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
            reverse("matching:check"),
            data=json.dumps({"matches": {}}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total"], 0)
