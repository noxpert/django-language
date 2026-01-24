# Migration to update initial words with native definitions and create Translation links

from django.db import migrations


def update_words_and_create_translations(apps, schema_editor):
    Language = apps.get_model("vocabulary", "Language")
    Word = apps.get_model("vocabulary", "Word")
    Translation = apps.get_model("vocabulary", "Translation")

    # Get languages
    english = Language.objects.get(code="en")
    hungarian = Language.objects.get(code="hu")
    german = Language.objects.get(code="de")

    # Create English words with English definitions
    en_book, _ = Word.objects.get_or_create(
        language=english,
        word="book",
        defaults={"definition": "A written or printed work consisting of pages bound together"}
    )
    en_house, _ = Word.objects.get_or_create(
        language=english,
        word="house",
        defaults={"definition": "A building for human habitation"}
    )
    en_water, _ = Word.objects.get_or_create(
        language=english,
        word="water",
        defaults={"definition": "A clear liquid essential for life"}
    )

    # Update Hungarian words with Hungarian definitions
    hu_book = Word.objects.get(language=hungarian, word="könyv")
    hu_book.definition = "Írott vagy nyomtatott mű, amelynek lapjai össze vannak kötve"
    hu_book.save()

    hu_house = Word.objects.get(language=hungarian, word="ház")
    hu_house.definition = "Épület, amelyben emberek laknak"
    hu_house.save()

    hu_water = Word.objects.get(language=hungarian, word="víz")
    hu_water.definition = "Tiszta folyadék, amely elengedhetetlen az élethez"
    hu_water.save()

    # Update German words with German definitions
    de_book = Word.objects.get(language=german, word="Buch")
    de_book.definition = "Ein geschriebenes oder gedrucktes Werk aus zusammengebundenen Seiten"
    de_book.save()

    de_house = Word.objects.get(language=german, word="Haus")
    de_house.definition = "Ein Gebäude zum Wohnen für Menschen"
    de_house.save()

    de_water = Word.objects.get(language=german, word="Wasser")
    de_water.definition = "Eine klare Flüssigkeit, die für das Leben unerlässlich ist"
    de_water.save()

    # Create Translation links
    # Hungarian <-> English
    Translation.objects.get_or_create(
        source_word=hu_book,
        target_word=en_book,
        defaults={'confidence': 'exact', 'notes': 'Initial data migration'}
    )
    Translation.objects.get_or_create(
        source_word=hu_house,
        target_word=en_house,
        defaults={'confidence': 'exact', 'notes': 'Initial data migration'}
    )
    Translation.objects.get_or_create(
        source_word=hu_water,
        target_word=en_water,
        defaults={'confidence': 'exact', 'notes': 'Initial data migration'}
    )

    # German <-> English
    Translation.objects.get_or_create(
        source_word=de_book,
        target_word=en_book,
        defaults={'confidence': 'exact', 'notes': 'Initial data migration'}
    )
    Translation.objects.get_or_create(
        source_word=de_house,
        target_word=en_house,
        defaults={'confidence': 'exact', 'notes': 'Initial data migration'}
    )
    Translation.objects.get_or_create(
        source_word=de_water,
        target_word=en_water,
        defaults={'confidence': 'exact', 'notes': 'Initial data migration'}
    )

    # Optional: Create Hungarian <-> German direct links
    Translation.objects.get_or_create(
        source_word=hu_book,
        target_word=de_book,
        defaults={'confidence': 'exact', 'notes': 'Initial data migration'}
    )
    Translation.objects.get_or_create(
        source_word=hu_house,
        target_word=de_house,
        defaults={'confidence': 'exact', 'notes': 'Initial data migration'}
    )
    Translation.objects.get_or_create(
        source_word=hu_water,
        target_word=de_water,
        defaults={'confidence': 'exact', 'notes': 'Initial data migration'}
    )


def reverse_migration(apps, schema_editor):
    """Remove English words and translations."""
    Language = apps.get_model("vocabulary", "Language")
    Word = apps.get_model("vocabulary", "Word")
    Translation = apps.get_model("vocabulary", "Translation")

    # Delete all translations
    Translation.objects.all().delete()

    # Delete English words
    english = Language.objects.get(code="en")
    Word.objects.filter(language=english).delete()

    # Reset Hungarian and German definitions to empty
    hungarian = Language.objects.get(code="hu")
    german = Language.objects.get(code="de")
    
    Word.objects.filter(language=hungarian).update(definition="")
    Word.objects.filter(language=german).update(definition="")


class Migration(migrations.Migration):

    dependencies = [
        ('vocabulary', '0007_rename_vocabulary_t_source__idx_vocabulary__source__7554cf_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(
            update_words_and_create_translations,
            reverse_migration
        ),
    ]
