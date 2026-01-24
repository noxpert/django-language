import pytest
from django.contrib.admin.sites import AdminSite

from vocabulary.admin import LanguageAdmin, WordAdmin, TranslationAdmin
from vocabulary.models import Language, Word, Translation


@pytest.mark.django_db
class TestLanguageAdmin:
    def test_list_display(self):
        """Test LanguageAdmin list_display configuration."""
        admin = LanguageAdmin(Language, AdminSite())
        assert "code" in admin.list_display
        assert "name" in admin.list_display
        # is_native removed in new model
        assert "is_native" not in admin.list_display

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
        assert "language" in admin.list_display
        assert "definition_preview" in admin.list_display
        assert "translation_count" in admin.list_display
        assert "added" in admin.list_display
        # translation field removed in new model
        assert "translation" not in admin.list_display

    def test_definition_preview_with_short_definition(self):
        """Test definition_preview with short definition."""
        language = Language.objects.create(code="hu", name="Hungarian")
        word = Word.objects.create(
            language=language,
            word="alma",
            definition="A fruit",
        )

        admin = WordAdmin(Word, AdminSite())
        preview = admin.definition_preview(word)
        assert preview == "A fruit"

    def test_definition_preview_with_long_definition(self):
        """Test definition_preview truncates long definitions."""
        language = Language.objects.create(code="hu", name="Hungarian")
        long_def = "A" * 60  # 60 character string
        word = Word.objects.create(
            language=language,
            word="alma",
            definition=long_def,
        )

        admin = WordAdmin(Word, AdminSite())
        preview = admin.definition_preview(word)
        assert len(preview) == 53  # 50 chars + "..."
        assert preview.endswith("...")

    def test_definition_preview_empty(self):
        """Test definition_preview with empty definition."""
        language = Language.objects.create(code="hu", name="Hungarian")
        word = Word.objects.create(
            language=language,
            word="ház",
            definition="",
        )

        admin = WordAdmin(Word, AdminSite())
        preview = admin.definition_preview(word)
        assert preview == "-"

    def test_translation_count_zero(self):
        """Test translation_count with no translations."""
        language = Language.objects.create(code="hu", name="Hungarian")
        word = Word.objects.create(language=language, word="alma")

        admin = WordAdmin(Word, AdminSite())
        count = admin.translation_count(word)
        assert count == "0 translations"

    def test_translation_count_one(self):
        """Test translation_count with one translation."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")

        Translation.objects.create(source_word=hu_word, target_word=en_word)

        admin = WordAdmin(Word, AdminSite())
        count = admin.translation_count(hu_word)
        assert count == "1 translation"

    def test_translation_count_multiple(self):
        """Test translation_count with multiple translations."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")
        german = Language.objects.create(code="de", name="German")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")
        de_word = Word.objects.create(language=german, word="Apfel")

        Translation.objects.create(source_word=hu_word, target_word=en_word)
        Translation.objects.create(source_word=hu_word, target_word=de_word)

        admin = WordAdmin(Word, AdminSite())
        count = admin.translation_count(hu_word)
        assert count == "2 translations"

    def test_translation_count_bidirectional(self):
        """Test translation_count counts both directions."""
        hungarian = Language.objects.create(code="hu", name="Hungarian")
        english = Language.objects.create(code="en", name="English")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")

        # Create translation in both directions
        Translation.objects.create(source_word=hu_word, target_word=en_word)
        Translation.objects.create(source_word=en_word, target_word=hu_word)

        admin = WordAdmin(Word, AdminSite())
        count = admin.translation_count(hu_word)
        assert count == "2 translations"

    def test_search_fields(self):
        """Test search fields configuration."""
        admin = WordAdmin(Word, AdminSite())
        assert "word" in admin.search_fields
        assert "definition" in admin.search_fields
        # translation removed from search fields
        assert "translation" not in admin.search_fields

    def test_has_inline(self):
        """Test that WordAdmin has TranslationInline."""
        admin = WordAdmin(Word, AdminSite())
        assert len(admin.inlines) == 1

    def test_readonly_fields(self):
        """Test readonly fields configuration."""
        admin = WordAdmin(Word, AdminSite())
        assert "added" in admin.readonly_fields
        assert "updated" in admin.readonly_fields


@pytest.mark.django_db
class TestTranslationAdmin:
    def test_list_display(self):
        """Test TranslationAdmin list_display configuration."""
        admin = TranslationAdmin(Translation, AdminSite())
        assert "source_word" in admin.list_display
        assert "target_word" in admin.list_display
        assert "confidence" in admin.list_display
        assert "created" in admin.list_display

    def test_list_filter(self):
        """Test list filter configuration."""
        admin = TranslationAdmin(Translation, AdminSite())
        assert "confidence" in admin.list_filter
        assert "created" in admin.list_filter

    def test_search_fields(self):
        """Test search fields configuration."""
        admin = TranslationAdmin(Translation, AdminSite())
        assert "source_word__word" in admin.search_fields
        assert "target_word__word" in admin.search_fields
        assert "notes" in admin.search_fields

    def test_readonly_fields(self):
        """Test readonly fields configuration."""
        admin = TranslationAdmin(Translation, AdminSite())
        assert "created" in admin.readonly_fields
        assert "updated" in admin.readonly_fields

    def test_autocomplete_fields(self):
        """Test autocomplete fields configuration."""
        admin = TranslationAdmin(Translation, AdminSite())
        assert "source_word" in admin.autocomplete_fields
        assert "target_word" in admin.autocomplete_fields

    def test_fieldsets(self):
        """Test fieldsets configuration."""
        admin = TranslationAdmin(Translation, AdminSite())
        assert len(admin.fieldsets) == 3

        # Translation Pair section
        assert admin.fieldsets[0][0] == "Translation Pair"
        assert "source_word" in admin.fieldsets[0][1]["fields"]
        assert "target_word" in admin.fieldsets[0][1]["fields"]

        # Details section
        assert admin.fieldsets[1][0] == "Details"
        assert "confidence" in admin.fieldsets[1][1]["fields"]
        assert "notes" in admin.fieldsets[1][1]["fields"]

        # Metadata section
        assert admin.fieldsets[2][0] == "Metadata"
        assert "created" in admin.fieldsets[2][1]["fields"]
        assert "updated" in admin.fieldsets[2][1]["fields"]
        assert "collapse" in admin.fieldsets[2][1]["classes"]
