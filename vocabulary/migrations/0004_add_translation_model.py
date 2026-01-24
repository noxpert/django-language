from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vocabulary", "0003_alter_word_definition"),
    ]

    operations = [
        migrations.CreateModel(
            name="Translation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("confidence", models.CharField(
                    choices=[
                        ("exact", "Exact translation"),
                        ("close", "Close meaning"),
                        ("approximate", "Approximate"),
                    ],
                    default="exact",
                    help_text="How closely these words match in meaning",
                    max_length=20
                )),
                ("notes", models.TextField(blank=True, default="", help_text="Context or usage notes for this translation pair")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("source_word", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="translations_from",
                    to="vocabulary.word"
                )),
                ("target_word", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="translations_to",
                    to="vocabulary.word"
                )),
            ],
        ),
        migrations.AddIndex(
            model_name="translation",
            index=models.Index(fields=["source_word", "target_word"], name="vocabulary_t_source__idx"),
        ),
        migrations.AlterUniqueTogether(
            name="translation",
            unique_together={("source_word", "target_word")},
        ),
    ]
