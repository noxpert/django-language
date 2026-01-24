import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from vocabulary.models import Language, Word, Translation


class Command(BaseCommand):
    help = "Import words and translations from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to CSV file with columns: language_code, word, translation, definition"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without actually importing"
        )
        parser.add_argument(
            "--skip-duplicates",
            action="store_true",
            help="Skip words that already exist instead of updating them"
        )
        parser.add_argument(
            "--target-language",
            type=str,
            default="en",
            help="Language code for translations (default: en for English)"
        )
        parser.add_argument(
            "--bidirectional",
            action="store_true",
            help="Create translations in both directions (A→B and B→A)"
        )
        parser.add_argument(
            "--confidence",
            type=str,
            choices=["exact", "close", "approximate"],
            default="exact",
            help="Translation confidence level (default: exact)"
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        dry_run = options["dry_run"]
        skip_duplicates = options["skip_duplicates"]
        target_lang_code = options["target_language"]
        bidirectional = options["bidirectional"]
        confidence = options["confidence"]

        # Check if file exists
        if not Path(csv_file).exists():
            raise CommandError(f"File not found: {csv_file}")

        # Get target language
        try:
            target_language = Language.objects.get(code=target_lang_code)
        except Language.DoesNotExist:
            raise CommandError(
                f"Target language '{target_lang_code}' not found. "
                f"Please create it first or specify a different --target-language"
            )

        stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "translations_created": 0
        }

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                # Validate required columns
                required_columns = {"language_code", "word", "translation", "definition"}
                if not required_columns.issubset(set(reader.fieldnames or [])):
                    raise CommandError(
                        f"CSV must contain columns: {", ".join(required_columns)}"
                    )

                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):
                        try:
                            result = self._process_row(
                                row,
                                target_language,
                                skip_duplicates,
                                dry_run,
                                bidirectional,
                                confidence
                            )
                            stats[result] += 1

                            # Count translations separately
                            if result == "created" and not dry_run:
                                # Check if translation was created
                                source_lang = Language.objects.get(code=row["language_code"])
                                source_word = Word.objects.get(
                                    language=source_lang,
                                    word=row["word"]
                                )
                                target_word = Word.objects.get(
                                    language=target_language,
                                    word=row["translation"]
                                )

                                # Count how many translations were created
                                trans_count = Translation.objects.filter(
                                    source_word=source_word,
                                    target_word=target_word
                                ).count()
                                if bidirectional:
                                    trans_count += Translation.objects.filter(
                                        source_word=target_word,
                                        target_word=source_word
                                    ).count()
                                stats["translations_created"] += trans_count

                        except Exception as e:
                            stats["errors"] += 1
                            self.stdout.write(
                                self.style.ERROR(f"Row {row_num}: Error - {str(e)}")
                            )

                    if dry_run:
                        # Rollback in dry-run mode
                        transaction.set_rollback(True)

        except Exception as e:
            raise CommandError(f"Error reading CSV file: {str(e)}")

        # Display summary
        self.stdout.write("\n" + "=" * 50)
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN SUMMARY"))
            self.stdout.write(f"Would create: {stats["created"]} words")
        else:
            self.stdout.write(self.style.SUCCESS("IMPORT SUMMARY"))
            self.stdout.write(f"Created:  {stats["created"]} words")
            self.stdout.write(f"Updated:  {stats["updated"]} words")
            self.stdout.write(f"Skipped:  {stats["skipped"]} words")
            self.stdout.write(f"Translations created: {stats["translations_created"]}")

        self.stdout.write(f"Errors:   {stats["errors"]}")
        self.stdout.write("=" * 50)

        if stats["errors"] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\nCompleted with {stats["errors"]} error(s). "
                    f"Check messages above for details."
                )
            )
        elif not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"\nSuccessfully imported {stats["created"]} words!")
            )

    def _process_row(self, row, target_language, skip_duplicates, dry_run,
                     bidirectional, confidence):
        """
        Process a single CSV row and create/update words and translations.
        Returns: "created", "updated", or "skipped"
        """
        language_code = row["language_code"].strip()
        word_text = row["word"].strip()
        translation_text = row["translation"].strip()
        definition = row.get("definition", "").strip()

        # Validate required fields
        if not language_code or not word_text or not translation_text:
            raise ValueError("Missing required field (language_code, word, or translation)")

        # Get source language
        try:
            source_language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            raise ValueError(f"Language '{language_code}' not found")

        # Check if source word already exists
        source_word = Word.objects.filter(
            language=source_language,
            word=word_text
        ).first()

        if source_word and skip_duplicates:
            return "skipped"

        if dry_run:
            self.stdout.write(
                f"Would create: {word_text} ({language_code}) → {translation_text} "
                f"({target_language.code})"
            )
            return "created"

        # Create or update source word
        if source_word:
            source_word.definition = definition
            source_word.save()
            action = "updated"
        else:
            source_word = Word.objects.create(
                language=source_language,
                word=word_text,
                definition=definition
            )
            action = "created"

        # Create or get target word (translation)
        target_word, created = Word.objects.get_or_create(
            language=target_language,
            word=translation_text,
            defaults={"definition": ""}
        )

        # Create translation link (source → target)
        Translation.objects.get_or_create(
            source_word=source_word,
            target_word=target_word,
            defaults={
                "confidence": confidence,
                "notes": "Imported from CSV"
            }
        )

        # Optionally create bidirectional translation (target → source)
        if bidirectional:
            Translation.objects.get_or_create(
                source_word=target_word,
                target_word=source_word,
                defaults={
                    "confidence": confidence,
                    "notes": "Imported from CSV (bidirectional)"
                }
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{action.capitalize()}: {word_text} ({language_code}) → "
                f"{translation_text} ({target_language.code})"
            )
        )

        return action
