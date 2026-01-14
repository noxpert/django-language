from django.db import models


class WordOfDay(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ja', 'Japanese'),
        ('zh', 'Chinese'),
        ('ko', 'Korean'),
        ('ru', 'Russian'),
    ]

    word = models.CharField(
        max_length=255,
        unique=True,
        help_text="The word to be featured"
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        help_text="Language of the word"
    )
    definition = models.TextField(
        help_text="Definition of the word"
    )
    pronunciation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="How the word is pronounced"
    )
    example_sentence = models.TextField(
        blank=True,
        null=True,
        help_text="Example sentence using the word"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this word was added"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this word was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Word of the Day"
        verbose_name_plural = "Words of the Day"

    def __str__(self):
        return f"{self.word} ({self.get_language_display()})"
