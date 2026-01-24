from django.db import models


class Language(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class WordManager(models.Manager):
    def random_words(self, language_code, count=10):
        """Get multiple random words for a specific language."""
        return self.filter(language__code=language_code).order_by("?")[:count]

    def for_language(self, language_code):
        """Get all words for a specific language."""
        return self.filter(language__code=language_code)


class Word(models.Model):
    """A word in a specific language with its native definition."""

    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name="words")
    word = models.CharField(max_length=100)
    definition = models.TextField(
        blank=True,
        default="",
        help_text="Definition in the same language as the word"
    )
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = WordManager()

    def __str__(self):
        return f"{self.word} ({self.language.code})"

    def get_translations(self, target_language=None):
        """
        Get all translations of this word.
        If target_language is specified, only return translations in that language.

        Returns a list of Word objects.
        """
        # Get translations where this word is the source
        translations_as_source = Translation.objects.filter(
            source_word=self
        ).select_related("target_word", "target_word__language")

        # Get translations where this word is the target
        translations_as_target = Translation.objects.filter(
            target_word=self
        ).select_related("source_word", "source_word__language")

        # Collect all translated words
        translated_words = []
        for trans in translations_as_source:
            if target_language is None or trans.target_word.language.code == target_language:
                translated_words.append(trans.target_word)

        for trans in translations_as_target:
            if target_language is None or trans.source_word.language.code == target_language:
                translated_words.append(trans.source_word)

        return translated_words

    def get_translation(self, target_language_code):
        """
        Get a single translation in a specific language.
        Returns the first match or None if no translation exists.
        """
        translations = self.get_translations(target_language=target_language_code)
        return translations[0] if translations else None

    def has_translation_to(self, target_language_code):
        """Check if this word has a translation in the specified language."""
        return bool(self.get_translation(target_language_code))

    class Meta:
        ordering = ["-added"]
        unique_together = ["language", "word"]


class Translation(models.Model):
    """
    Junction table linking words across languages.
    Bidirectional relationship: if A translates to B, then B translates to A.
    """

    source_word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name="translations_from"
    )
    target_word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name="translations_to"
    )
    confidence = models.CharField(
        max_length=20,
        choices=[
            ("exact", "Exact translation"),
            ("close", "Close meaning"),
            ("approximate", "Approximate"),
        ],
        default="exact",
        help_text="How closely these words match in meaning"
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Context or usage notes for this translation pair"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source_word.word} → {self.target_word.word}"

    def clean(self):
        """Ensure words are in different languages."""
        from django.core.exceptions import ValidationError
        if self.source_word.language == self.target_word.language:
            raise ValidationError("Cannot translate a word to the same language")

    class Meta:
        unique_together = ["source_word", "target_word"]
        indexes = [
            models.Index(fields=["source_word", "target_word"]),
        ]
