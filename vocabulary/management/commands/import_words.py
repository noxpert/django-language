import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from vocabulary.models import Language, Word


class Command(BaseCommand):
    help = """
    Import vocabulary words from a CSV file.

    CSV Format (with header row):
        language_code,word,translation,definition

    Example CSV content:
        language_code,word,translation,definition
        hu,alma,apple,A fruit that grows on trees
        hu,ház,house,
        de,Buch,book,A written work

    Notes:
        - Definition column is optional (can be empty)
        - Language code must exist in database (en, hu, de)
        - Duplicate words will be skipped
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to CSV file containing words to import",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview import without making changes",
        )
        parser.add_argument(
            "--skip-duplicates",
            action="store_true",
            default=True,
            help="Skip words that already exist (default: True)",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        dry_run = options["dry_run"]
        skip_duplicates = options["skip_duplicates"]

        # Validate file exists
        file_path = Path(csv_file)
        if not file_path.exists():
            raise CommandError(f"File not found: {csv_file}")

        # Read and validate CSV
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                # Validate required columns
                required_columns = {"language_code", "word", "translation"}
                if not required_columns.issubset(reader.fieldnames or []):
                    raise CommandError(
                        f"CSV must contain columns: {', '.join(required_columns)}"
                    )

                # Process rows
                stats = {
                    "created": 0,
                    "skipped": 0,
                    "errors": 0,
                }

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 (header is 1)
                    try:
                        self._process_row(row, row_num, dry_run, skip_duplicates, stats)
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Row {row_num}: Error - {str(e)}")
                        )
                        stats["errors"] += 1

        except Exception as e:
            raise CommandError(f"Failed to read CSV: {str(e)}")

        # Display summary
        self._display_summary(stats, dry_run)

    def _process_row(self, row, row_num, dry_run, skip_duplicates, stats):
        """Process a single CSV row."""
        language_code = row.get("language_code", "").strip()
        word_text = row.get("word", "").strip()
        translation = row.get("translation", "").strip()
        definition = row.get("definition", "").strip()

        # Validate required fields
        if not all([language_code, word_text, translation]):
            raise ValueError("Missing required fields")

        # Get language
        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            raise ValueError(f"Language '{language_code}' not found")

        # Check for duplicates
        if skip_duplicates:
            exists = Word.objects.filter(
                language=language, word=word_text, translation=translation
            ).exists()
            if exists:
                self.stdout.write(
                    self.style.WARNING(
                        f"Row {row_num}: Skipped duplicate - {word_text} ({language_code})"
                    )
                )
                stats["skipped"] += 1
                return

        # Create word
        if not dry_run:
            Word.objects.create(
                language=language,
                word=word_text,
                translation=translation,
                definition=definition,
            )

        definition_note = " [with definition]" if definition else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"Row {row_num}: {'Would create' if dry_run else 'Created'} - "
                f"{word_text} → {translation} ({language_code}){definition_note}"
            )
        )
        stats["created"] += 1

    def _display_summary(self, stats, dry_run):
        """Display import summary statistics."""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS(f"{'DRY RUN - ' if dry_run else ''}Import Summary:")
        )
        self.stdout.write(f"  Created: {stats['created']}")
        self.stdout.write(f"  Skipped: {stats['skipped']}")
        self.stdout.write(f"  Errors:  {stats['errors']}")
        self.stdout.write("=" * 50)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nThis was a dry run. No changes were made to the database."
                )
            )
            self.stdout.write("Run without --dry-run to import words.")
