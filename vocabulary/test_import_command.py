import tempfile
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from vocabulary.models import Language, Word


@pytest.mark.django_db
class TestImportWordsCommand:
    @pytest.fixture
    def setup_languages(self):
        """Create test languages."""
        Language.objects.create(code="en", name="English", is_native=True)
        Language.objects.create(code="hu", name="Hungarian", is_native=False)
        Language.objects.create(code="de", name="German", is_native=False)

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
hu,alma,apple,A fruit that grows on trees
hu,ház,house,A building for habitation
de,Buch,book,A written work"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, stdout=out)

            assert Word.objects.count() == 3
            assert Word.objects.filter(word="alma").exists()
            assert Word.objects.filter(word="ház").exists()
            assert Word.objects.filter(word="Buch").exists()

            output = out.getvalue()
            assert "Created: 3" in output
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

            assert Word.objects.count() == 2

            water_hu = Word.objects.get(word="víz")
            assert water_hu.definition == ""

            water_de = Word.objects.get(word="Wasser")
            assert water_de.definition == ""
        finally:
            Path(csv_file).unlink()

    def test_dry_run(self, setup_languages, create_csv):
        """Test dry-run mode doesn't create records."""
        csv_content = """language_code,word,translation,definition
hu,teszt,test,Test word"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, "--dry-run", stdout=out)

            assert Word.objects.count() == 0
            output = out.getvalue()
            assert "Would create" in output
            assert "DRY RUN" in output
        finally:
            Path(csv_file).unlink()

    def test_skip_duplicates(self, setup_languages, create_csv):
        """Test skipping duplicate words."""
        language = Language.objects.get(code="hu")
        Word.objects.create(
            language=language, word="alma", translation="apple", definition=""
        )

        csv_content = """language_code,word,translation,definition
hu,alma,apple,A fruit
hu,ház,house,A building"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, "--skip-duplicates", stdout=out)

            assert Word.objects.count() == 2  # 1 existing + 1 new
            output = out.getvalue()
            assert "Skipped: 1" in output
            assert "Created: 1" in output
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

            assert Word.objects.count() == 0
            output = out.getvalue()
            assert "Error" in output
            assert "Errors:  1" in output
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
            assert "Error" in output
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

            assert "must contain columns" in str(exc_info.value)
        finally:
            Path(csv_file).unlink()

    def test_file_not_found(self, setup_languages):
        """Test error when CSV file doesn't exist."""
        with pytest.raises(CommandError) as exc_info:
            call_command("import_words", "/nonexistent/file.csv")

        assert "File not found" in str(exc_info.value)

    def test_mixed_results(self, setup_languages, create_csv):
        """Test import with mix of success, skips, and errors."""
        language = Language.objects.get(code="hu")
        Word.objects.create(
            language=language, word="alma", translation="apple", definition=""
        )

        csv_content = """language_code,word,translation,definition
hu,alma,apple,Duplicate
hu,ház,house,Valid
xx,invalid,word,Bad language
hu,víz,water,Valid"""

        csv_file = create_csv(csv_content)

        try:
            out = StringIO()
            call_command("import_words", csv_file, stdout=out)

            assert Word.objects.count() == 3  # 1 existing + 2 new
            output = out.getvalue()
            assert "Created: 2" in output
            assert "Skipped: 1" in output
            assert "Errors:  1" in output
        finally:
            Path(csv_file).unlink()
