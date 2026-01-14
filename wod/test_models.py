import pytest

from wod.models import Language, Word


@pytest.mark.django_db
class TestLanguageModel:
    def test_create_language(self):
        language = Language.objects.create(
            code="es", name="Spanish", is_native=False
        )
        assert language.code == "es"
        assert language.name == "Spanish"
        assert language.is_native is False

    def test_language_str(self):
        language = Language.objects.create(
            code="fr", name="French", is_native=False
        )
        assert str(language) == "French"

    def test_language_code_unique(self):
        Language.objects.create(code="de", name="German", is_native=False)
        with pytest.raises(Exception):
            Language.objects.create(code="de", name="German Duplicate", is_native=False)


@pytest.mark.django_db
class TestWordModel:
    def test_create_word(self):
        language = Language.objects.create(
            code="hu", name="Hungarian", is_native=False
        )
        word = Word.objects.create(
            language=language,
            word="alma",
            translation="apple",
            definition="A fruit that grows on trees",
        )
        assert word.word == "alma"
        assert word.translation == "apple"
        assert word.language == language
        assert word.added is not None
        assert word.updated is not None

    def test_word_str(self):
        language = Language.objects.create(
            code="de", name="German", is_native=False
        )
        word = Word.objects.create(
            language=language,
            word="Apfel",
            translation="apple",
            definition="A fruit",
        )
        assert str(word) == "Apfel (de)"

    def test_word_ordering(self):
        language = Language.objects.create(
            code="hu", name="Hungarian", is_native=False
        )
        word1 = Word.objects.create(
            language=language,
            word="első",
            translation="first",
            definition="First word",
        )
        word2 = Word.objects.create(
            language=language,
            word="második",
            translation="second",
            definition="Second word",
        )
        words = Word.objects.all()
        assert words[0] == word2
        assert words[1] == word1
