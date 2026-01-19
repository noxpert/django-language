from django.contrib import admin

from .models import Language, Word


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """
    Admin interface for Language model.

    Manage the supported languages (English, Hungarian, German).
    Mark your native language with the 'is_native' checkbox.
    """

    list_display = ["code", "name", "is_native", "word_count"]
    list_filter = ["is_native"]
    search_fields = ["code", "name"]
    ordering = ["name"]

    def word_count(self, obj):
        """Display the number of words for this language."""
        return obj.word_set.count()

    word_count.short_description = "Word Count"


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """
    Admin interface for Word model.

    Add and edit vocabulary words with translations.
    Definition is optional - you can add it later.
    For bulk imports, use: python manage.py import_words <file.csv>
    """

    list_display = ["word", "translation", "language", "has_definition", "added"]
    list_filter = ["language", "added"]
    search_fields = ["word", "translation", "definition"]
    ordering = ["-added"]
    date_hierarchy = "added"

    fieldsets = [
        (
            None,
            {
                "fields": ["language", "word", "translation"],
                "description": "Required fields for each vocabulary word.",
            },
        ),
        (
            "Optional Details",
            {
                "fields": ["definition"],
                "description": "Add a definition to provide more context (optional).",
                "classes": ["collapse"],
            },
        ),
    ]

    def has_definition(self, obj):
        """Show if word has a definition."""
        return bool(obj.definition)

    has_definition.boolean = True
    has_definition.short_description = "Has Definition"
