import pytest
from django.core.exceptions import ValidationError

from vocabulary.models import Language, Word, Translation


@pytest.mark.django_db
class TestLanguageModel:
    def test_create_language(self):
        language = Language.objects.create(code="es", name="Spanish")
        assert language.code == "es"
        assert language.name == "Spanish"

    def test_language_str(self):
        language = Language.objects.create(code="fr", name="French")
        assert str(language) == "French"

    def test_language_code_unique(self):
        Language.objects.create(code="de", name="German")
        with pytest.raises(Exception):
            Language.objects.create(code="de", name="German Duplicate")

    def test_language_ordering(self):
        """Test languages are ordered by name."""
        Language.objects.create(code="de", name="German")
        Language.objects.create(code="en", name="English")
        Language.objects.create(code="hu", name="Hungarian")

        languages = list(Language.objects.all())
        assert languages[0].name == "English"
        assert languages[1].name == "German"
        assert languages[2].name == "Hungarian"


@pytest.mark.django_db
class TestWordModel:
    def test_create_word(self):
        language = Language.objects.create(code="hu", name="Hungarian")
        word = Word.objects.create(
            language=language,
            word="alma",
            definition="A fruit that grows on trees",
        )
        assert word.word == "alma"
        assert word.language == language
        assert word.definition == "A fruit that grows on trees"
        assert word.added is not None
        assert word.updated is not None

    def test_word_str(self):
        language = Language.objects.create(code="de", name="German")
        word = Word.objects.create(
            language=language,
            word="Apfel",
            definition="A fruit",
        )
        assert str(word) == "Apfel (de)"

    def test_word_ordering(self):
        """Test words are ordered by added date (newest first)."""
        language = Language.objects.create(code="hu", name="Hungarian")
        word1 = Word.objects.create(
            language=language,
            word="első",
            definition="First word",
        )
        word2 = Word.objects.create(
            language=language,
            word="második",
            definition="Second word",
        )
        words = Word.objects.all()
        assert words[0] == word2
        assert words[1] == word1

    def test_create_word_without_definition(self):
        language = Language.objects.create(code="hu", name="Hungarian")
        word = Word.objects.create(
            language=language,
            word="víz",
        )
        assert word.word == "víz"
        assert word.definition == ""
        assert word.language == language

    def test_unique_together_constraint(self):
        """Test that same word cannot be added twice for same language."""
        language = Language.objects.create(code="hu", name="Hungarian")
        Word.objects.create(language=language, word="alma")

        with pytest.raises(Exception):  # IntegrityError
            Word.objects.create(language=language, word="alma")

    def test_same_word_different_languages(self):
        """Test same word can exist in different languages."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        german = Language.objects.create(code="de", name="German")

        word1 = Word.objects.create(language=hungarian, word="tag")
        word2 = Word.objects.create(language=german, word="tag")

        assert word1.id != word2.id
        assert Word.objects.filter(word="tag").count() == 2


@pytest.mark.django_db
class TestWordManager:
    def test_random_words(self):
        """Test getting multiple random words."""
        language = Language.objects.create(code="hu", name="Hungarian")
        for i in range(10):
            Word.objects.create(language=language, word=f"word{i}")

        random_words = Word.objects.random_words("hu", count=5)
        assert len(random_words) == 5
        for word in random_words:
            assert word.language.code == "hu"

    def test_random_words_fewer_than_count(self):
        """Test random_words when fewer words exist than requested."""
        language = Language.objects.create(code="hu", name="Hungarian")
        Word.objects.create(language=language, word="alma")
        Word.objects.create(language=language, word="körte")

        random_words = Word.objects.random_words("hu", count=5)
        assert len(random_words) == 2

    def test_for_language(self):
        """Test getting all words for a language."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        german = Language.objects.create(code="de", name="German")

        Word.objects.create(language=hungarian, word="alma")
        Word.objects.create(language=hungarian, word="körte")
        Word.objects.create(language=german, word="Apfel")

        hu_words = Word.objects.for_language("hu")
        assert hu_words.count() == 2
        assert all(w.language.code == "hu" for w in hu_words)


@pytest.mark.django_db
class TestTranslationModel:
    def test_create_translation(self):
        """Test creating a translation between two words."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")

        translation = Translation.objects.create(
            source_word=hu_word,
            target_word=en_word,
            confidence="exact"
        )

        assert translation.source_word == hu_word
        assert translation.target_word == en_word
        assert translation.confidence == "exact"
        assert translation.created is not None

    def test_translation_str(self):
        """Test translation string representation."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")

        translation = Translation.objects.create(
            source_word=hu_word,
            target_word=en_word
        )

        assert str(translation) == "alma → apple"

    def test_translation_with_notes(self):
        """Test creating translation with notes."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="ház")
        en_word = Word.objects.create(language=english, word="house")

        translation = Translation.objects.create(
            source_word=hu_word,
            target_word=en_word,
            confidence="close",
            notes="Can also mean 'building' in some contexts"
        )

        assert translation.notes == "Can also mean 'building' in some contexts"
        assert translation.confidence == "close"

    def test_translation_same_language_validation(self):
        """Test that translation validates words are in different languages."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")

        word1 = Word.objects.create(language=hungarian, word="alma")
        word2 = Word.objects.create(language=hungarian, word="körte")

        translation = Translation(source_word=word1, target_word=word2)

        with pytest.raises(ValidationError):
            translation.clean()

    def test_unique_translation_pair(self):
        """Test that same translation pair cannot be created twice."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")

        Translation.objects.create(source_word=hu_word, target_word=en_word)

        with pytest.raises(Exception):  # IntegrityError
            Translation.objects.create(source_word=hu_word, target_word=en_word)

    def test_bidirectional_translations_allowed(self):
        """Test that bidirectional translations (A→B and B→A) are allowed."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")

        trans1 = Translation.objects.create(source_word=hu_word, target_word=en_word)
        trans2 = Translation.objects.create(source_word=en_word, target_word=hu_word)

        assert trans1.id != trans2.id
        assert Translation.objects.count() == 2


@pytest.mark.django_db
class TestWordTranslationMethods:
    def test_get_translations(self):
        """Test getting all translations of a word."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        german = Language.objects.create(code="de", name="German")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")
        de_word = Word.objects.create(language=german, word="Apfel")

        Translation.objects.create(source_word=hu_word, target_word=en_word)
        Translation.objects.create(source_word=hu_word, target_word=de_word)

        translations = hu_word.get_translations()
        assert len(translations) == 2
        assert en_word in translations
        assert de_word in translations

    def test_get_translations_specific_language(self):
        """Test getting translations in a specific language."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        german = Language.objects.create(code="de", name="German")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")
        de_word = Word.objects.create(language=german, word="Apfel")

        Translation.objects.create(source_word=hu_word, target_word=en_word)
        Translation.objects.create(source_word=hu_word, target_word=de_word)

        en_translations = hu_word.get_translations(target_language="en")
        assert len(en_translations) == 1
        assert en_translations[0] == en_word

    def test_get_translation(self):
        """Test getting single translation in specific language."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")

        Translation.objects.create(source_word=hu_word, target_word=en_word)

        translation = hu_word.get_translation("en")
        assert translation == en_word

    def test_get_translation_none(self):
        """Test get_translation returns None when no translation exists."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        Language.objects.create(code="de", name="German")

        hu_word = Word.objects.create(language=hungarian, word="alma")

        translation = hu_word.get_translation("de")
        assert translation is None

    def test_has_translation_to(self):
        """Test checking if translation exists to specific language."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        Language.objects.create(code="de", name="German")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")

        Translation.objects.create(source_word=hu_word, target_word=en_word)

        assert hu_word.has_translation_to("en") is True
        assert hu_word.has_translation_to("de") is False

    def test_bidirectional_get_translations(self):
        """Test that get_translations works regardless of which word is source/target."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")

        # Create translation with Hungarian as source
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        # Should work from both directions
        assert en_word in hu_word.get_translations()
        assert hu_word in en_word.get_translations()

    def test_get_translations_empty(self):
        """Test get_translations returns empty list when no translations exist."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        hu_word = Word.objects.create(language=hungarian, word="alma")

        translations = hu_word.get_translations()
        assert translations == []
