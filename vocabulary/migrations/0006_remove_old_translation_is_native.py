from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("vocabulary", "0005_migrate_translation_data"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="word",
            name="translation",
        ),
        # Remove is_native field from Language model
        migrations.RemoveField(
            model_name="language",
            name="is_native",
        ),
    ]
