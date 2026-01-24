from django.contrib import admin
from .models import Language, Word, Translation


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """
    Admin interface for Language model.

    Manage the supported languages (English, Hungarian, German).
    """

    list_display = ["code", "name"]
    search_fields = ["code", "name"]


class TranslationInline(admin.TabularInline):
    """Show translations inline when editing a word."""
    model = Translation
    fk_name = "source_word"
    extra = 1
    autocomplete_fields = ["target_word"]
    fields = ["target_word", "confidence", "notes"]


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """
    Admin interface for Word model.

    Add and edit vocabulary words.
    Definition is optional - you can add it later.
    For bulk imports, use: python manage.py import_words <file.csv>
    """
    list_display = ["word", "language", "definition_preview", "translation_count", "added"]
    list_filter = ["language", "added"]
    search_fields = ["word", "definition"]
    autocomplete_fields = ["language"]
    readonly_fields = ["added", "updated"]
    inlines = [TranslationInline]

    def definition_preview(self, obj):
        """Show truncated definition."""
        if obj.definition:
            return obj.definition[:50] + "..." if len(obj.definition) > 50 else obj.definition
        return "-"

    definition_preview.short_description = "Definition"

    def translation_count(self, obj):
        """Show number of translations."""
        count_from = obj.translations_from.count()
        count_to = obj.translations_to.count()
        total = count_from + count_to
        return f"{total} translation{"s" if total != 1 else ""}"

    translation_count.short_description = "Translations"


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ["source_word", "target_word", "confidence", "created"]
    list_filter = ["confidence", "created"]
    search_fields = ["source_word__word", "target_word__word", "notes"]
    autocomplete_fields = ["source_word", "target_word"]
    readonly_fields = ["created", "updated"]
    fieldsets = [
        ("Translation Pair", {
            "fields": ["source_word", "target_word"]
        }),
        ("Details", {
            "fields": ["confidence", "notes"]
        }),
        ("Metadata", {
            "fields": ["created", "updated"],
            "classes": ["collapse"]
        }),
    ]
