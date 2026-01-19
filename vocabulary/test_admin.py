import pytest
from django.contrib.admin.sites import AdminSite

from vocabulary.admin import LanguageAdmin, WordAdmin
from vocabulary.models import Language, Word


@pytest.mark.django_db
class TestLanguageAdmin:
    def test_list_display(self):
        """Test LanguageAdmin list_display configuration."""
        admin = LanguageAdmin(Language, AdminSite())
        assert "code" in admin.list_display
        assert "name" in admin.list_display
        assert "is_native" in admin.list_display
        assert "word_count" in admin.list_display

    def test_word_count_display(self):
        """Test word_count method returns correct count."""
        language = Language.objects.create(code="hu", name="Hungarian")
        Word.objects.create(
            language=language, word="alma", translation="apple", definition=""
        )
        Word.objects.create(
            language=language, word="ház", translation="house", definition=""
        )

        admin = LanguageAdmin(Language, AdminSite())
        assert admin.word_count(language) == 2

    def test_word_count_zero(self):
        """Test word_count returns 0 for language with no words."""
        language = Language.objects.create(code="de", name="German")
        admin = LanguageAdmin(Language, AdminSite())
        assert admin.word_count(language) == 0

    def test_search_fields(self):
        """Test search fields configuration."""
        admin = LanguageAdmin(Language, AdminSite())
        assert "code" in admin.search_fields
        assert "name" in admin.search_fields


@pytest.mark.django_db
class TestWordAdmin:
    def test_list_display(self):
        """Test WordAdmin list_display configuration."""
        admin = WordAdmin(Word, AdminSite())
        assert "word" in admin.list_display
        assert "translation" in admin.list_display
        assert "language" in admin.list_display
        assert "has_definition" in admin.list_display
        assert "added" in admin.list_display

    def test_has_definition_true(self):
        """Test has_definition returns True when definition exists."""
        language = Language.objects.create(code="hu", name="Hungarian")
        word = Word.objects.create(
            language=language,
            word="alma",
            translation="apple",
            definition="A fruit that grows on trees",
        )

        admin = WordAdmin(Word, AdminSite())
        assert admin.has_definition(word) is True

    def test_has_definition_false(self):
        """Test has_definition returns False when definition is empty."""
        language = Language.objects.create(code="hu", name="Hungarian")
        word = Word.objects.create(
            language=language, word="ház", translation="house", definition=""
        )

        admin = WordAdmin(Word, AdminSite())
        assert admin.has_definition(word) is False

    def test_search_fields(self):
        """Test search fields configuration."""
        admin = WordAdmin(Word, AdminSite())
        assert "word" in admin.search_fields
        assert "translation" in admin.search_fields
        assert "definition" in admin.search_fields

    def test_fieldsets(self):
        """Test fieldsets configuration."""
        admin = WordAdmin(Word, AdminSite())
        assert len(admin.fieldsets) == 2

        # Required fields section
        assert admin.fieldsets[0][1]["fields"] == [
            "language",
            "word",
            "translation",
        ]

        # Optional details section
        assert admin.fieldsets[1][1]["fields"] == ["definition"]
        assert "collapse" in admin.fieldsets[1][1]["classes"]
