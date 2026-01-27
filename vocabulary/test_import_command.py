import tempfile
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from vocabulary.models import Language, Translation, Word


@pytest.mark.django_db
class TestImportWordsCommand:
    @pytest.fixture
    def setup_languages(self):
        """Create test languages."""
        Language.objects.create(code="en", name="English")
        Language.objects.create(code="hu", name="Hungarian")
        Language.objects.create(code="de", name="German")

    @pytest.fixture
    def create_csv(self):
        """Helper to create temporary CSV files."""

        def _create_csv(content):
            temp_file = tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".csv", encoding="utf-8"
            )
            temp_file.write(content)
            temp_file.close()
            return temp_file.name

        return _create_csv

    def test_import_valid_csv(self, setup_languages, create_csv):
        """Test importing valid CSV with all fields."""
        csv_content = """language_code,word,translation,definition
hu,alma,apple,Egy gyümölcs amely fán terem
hu,ház,house,Épület lakás céljára
de,Buch,book,Ein schriftliches Werk"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, stdout=out)

            # Should create 6 words (3 in source language + 3 in English)
            # and 3 translations
            assert Word.objects.filter(word="alma").exists()
            assert Word.objects.filter(word="apple").exists()
            assert Word.objects.filter(word="ház").exists()
            assert Word.objects.filter(word="house").exists()
            assert Word.objects.filter(word="Buch").exists()
            assert Word.objects.filter(word="book").exists()

            # Check translations were created
            alma = Word.objects.get(word="alma")
            apple = Word.objects.get(word="apple")
            assert Translation.objects.filter(
                source_word=alma, target_word=apple
            ).exists()

            output = out.getvalue()
            assert "Created" in output
        finally:
            Path(csv_file).unlink()

    def test_import_without_definition(self, setup_languages, create_csv):
        """Test importing words without definitions."""
        csv_content = """language_code,word,translation,definition
hu,víz,water,
de,Wasser,water,"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, stdout=out)

            water_hu = Word.objects.get(word="víz")
            assert water_hu.definition == ""

            water_de = Word.objects.get(word="Wasser")
            assert water_de.definition == ""

            # Check translations created
            water_en = Word.objects.get(word="water")
            assert Translation.objects.filter(
                source_word=water_hu, target_word=water_en
            ).exists()
        finally:
            Path(csv_file).unlink()

    def test_dry_run(self, setup_languages, create_csv):
        """Test dry-run mode doesn"t create records."""
        csv_content = """language_code,word,translation,definition
hu,teszt,test,Teszt szó"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, "--dry-run", stdout=out)

            assert Word.objects.count() == 0
            assert Translation.objects.count() == 0
            output = out.getvalue()
            assert "Would create" in output or "DRY RUN" in output
        finally:
            Path(csv_file).unlink()

    def test_skip_duplicates(self, setup_languages, create_csv):
        """Test skipping duplicate words."""
        hungarian = Language.objects.get(code="hu")
        english = Language.objects.get(code="en")

        # Create existing word and translation
        hu_word = Word.objects.create(language=hungarian, word="alma", definition="")
        en_word = Word.objects.create(language=english, word="apple", definition="")
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        csv_content = """language_code,word,translation,definition
hu,alma,apple,A fruit
hu,ház,house,A building"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, "--skip-duplicates", stdout=out)

            # Should only create ház/house pair, skip alma/apple
            assert Word.objects.filter(word="ház").exists()
            assert Word.objects.filter(word="house").exists()

            output = out.getvalue()
            assert "Skipped" in output or "skip" in output.lower()
        finally:
            Path(csv_file).unlink()

    def test_invalid_language_code(self, setup_languages, create_csv):
        """Test error handling for invalid language code."""
        csv_content = """language_code,word,translation,definition
xx,invalid,word,Test"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, stdout=out)

            # Should not create any words
            assert Word.objects.count() == 0
            assert Translation.objects.count() == 0

            output = out.getvalue()
            assert "Error" in output or "error" in output.lower()
        finally:
            Path(csv_file).unlink()

    def test_missing_required_field(self, setup_languages, create_csv):
        """Test error handling for missing required fields."""
        csv_content = """language_code,word,translation,definition
hu,,apple,A fruit"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, stdout=out)

            assert Word.objects.count() == 0
            output = out.getvalue()
            assert "Error" in output or "error" in output.lower()
        finally:
            Path(csv_file).unlink()

    def test_missing_csv_columns(self, setup_languages, create_csv):
        """Test error when CSV is missing required columns."""
        csv_content = """language_code,word
hu,alma"""

        csv_file = create_csv(csv_content)

        try:
            with pytest.raises(CommandError) as exc_info:
                call_command("import_words", csv_file)

            assert (
                "must contain columns" in str(exc_info.value).lower()
                or "missing" in str(exc_info.value).lower()
            )
        finally:
            Path(csv_file).unlink()

    def test_file_not_found(self, setup_languages):
        """Test error when CSV file doesn"t exist."""
        with pytest.raises(CommandError) as exc_info:
            call_command("import_words", "/nonexistent/file.csv")

        assert (
            "File not found" in str(exc_info.value)
            or "not found" in str(exc_info.value).lower()
        )

    def test_mixed_results(self, setup_languages, create_csv):
        """Test import with mix of success, skips, and errors."""
        hungarian = Language.objects.get(code="hu")
        english = Language.objects.get(code="en")

        hu_word = Word.objects.create(language=hungarian, word="alma")
        en_word = Word.objects.create(language=english, word="apple")
        Translation.objects.create(source_word=hu_word, target_word=en_word)

        csv_content = """language_code,word,translation,definition
hu,alma,apple,Duplicate
hu,ház,house,Valid
xx,invalid,word,Bad language
hu,víz,water,Valid"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, stdout=out)

            # Should create ház/house and víz/water pairs
            assert Word.objects.filter(word="ház").exists()
            assert Word.objects.filter(word="víz").exists()

            output = out.getvalue()
            # Should report some combination of created/skipped/errors
            assert any(
                word in output.lower() for word in ["created", "skipped", "error"]
            )
        finally:
            Path(csv_file).unlink()


@pytest.mark.django_db
class TestImportTranslationCreation:
    """Test that import command creates proper Translation objects."""

    @pytest.fixture
    def setup_languages(self):
        Language.objects.create(code="en", name="English")
        Language.objects.create(code="hu", name="Hungarian")

    @pytest.fixture
    def create_csv(self):
        def _create_csv(content):
            temp_file = tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".csv", encoding="utf-8"
            )
            temp_file.write(content)
            temp_file.close()
            return temp_file.name

        return _create_csv

    def test_creates_bidirectional_translations(self, setup_languages, create_csv):
        """Test that import optionally creates bidirectional translations."""
        csv_content = """language_code,word,translation,definition
hu,alma,apple,Gyümölcs"""

        csv_file = create_csv(csv_content)

        try:
            call_command("import_words", csv_file)

            hu_word = Word.objects.get(word="alma")
            en_word = Word.objects.get(word="apple")

            # Check at least one direction exists
            assert (
                Translation.objects.filter(
                    source_word=hu_word, target_word=en_word
                ).exists()
                or Translation.objects.filter(
                    source_word=en_word, target_word=hu_word
                ).exists()
            )
        finally:
            Path(csv_file).unlink()

    def test_translation_confidence_default(self, setup_languages, create_csv):
        """Test that imported translations have default confidence."""
        csv_content = """language_code,word,translation,definition
hu,ház,house,Épület"""

        csv_file = create_csv(csv_content)

        try:
            call_command("import_words", csv_file)

            translation = Translation.objects.first()
            assert translation is not None
            assert translation.confidence in ["exact", "close", "approximate"]
        finally:
            Path(csv_file).unlink()
