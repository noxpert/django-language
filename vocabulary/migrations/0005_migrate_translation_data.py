from django.db import migrations


def migrate_translations(apps, schema_editor):
    """
    Migrate data from old Word.translation field to new Translation model.

    For each Word with a translation:
    1. Create or find the English word that matches the translation
    2. Create a Translation linking them
    """
    Word = apps.get_model("vocabulary", "Word")
    Translation = apps.get_model("vocabulary", "Translation")
    Language = apps.get_model("vocabulary", "Language")

    # Get or create English language (assuming translations are in English)
    # Adjust this if your translations are in a different language
    english, _ = Language.objects.get_or_create(
        code="en",
        defaults={"name": "English"}
    )

    migrated_count = 0
    skipped_count = 0

    # Process each word that has a translation
    for word in Word.objects.exclude(translation="").exclude(translation__isnull=True):
        try:
            # Create or get the English word for this translation
            english_word, created = Word.objects.get_or_create(
                language=english,
                word=word.translation,
                defaults={
                    "definition": "",  # Can be filled in later
                }
            )

            # Create the translation link (only if it doesn"t already exist)
            Translation.objects.get_or_create(
                source_word=word,
                target_word=english_word,
                defaults={
                    "confidence": "exact",
                    "notes": "Migrated from old translation field"
                }
            )

            migrated_count += 1

        except Exception as e:
            print(f"Error migrating word '{word.word}': {e}")
            skipped_count += 1
            continue

    print(f"Migration complete: {migrated_count} translations created, {skipped_count} skipped")


def reverse_migration(apps, schema_editor):
    """
    Reverse migration: populate Word.translation from Translation model.
    This is a best-effort reversal and may lose some data.
    """
    Word = apps.get_model("vocabulary", "Word")
    Translation = apps.get_model("vocabulary", "Translation")
    Language = apps.get_model("vocabulary", "Language")

    try:
        english = Language.objects.get(code="en")
    except Language.DoesNotExist:
        print("Warning: English language not found, cannot reverse migration")
        return

    for translation in Translation.objects.all():
        # If source word"s translation is empty, populate it
        if not translation.source_word.translation:
            # Assuming target is English
            if translation.target_word.language == english:
                translation.source_word.translation = translation.target_word.word
                translation.source_word.save()


class Migration(migrations.Migration):
    dependencies = [
        ("vocabulary", "0004_add_translation_model"),
    ]

    operations = [
        migrations.RunPython(migrate_translations, reverse_migration),
    ]
