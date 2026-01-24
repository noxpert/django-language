from django.shortcuts import render
from django.db.models import Count

from vocabulary.models import Language, Word


def random_word(request):
    # Only show languages that have words
    languages = Language.objects.annotate(
        word_count=Count("words")
    ).filter(word_count__gt=0)

    selected_language = request.GET.get("language")
    word = None
    translation = None

    if selected_language:
        # Get a random word in the selected language
        words = Word.objects.random_words(selected_language, 1)

        if words:  # Check if any words were returned
            word = words[0]
            # Get English translation
            en_translation = word.get_translation("en")
            translation = en_translation.word if en_translation else "No translation"

    return render(
        request,
        "wod/random_word.html",
        {
            "word": word,
            "translation": translation,
            "languages": languages,
            "selected_language": selected_language,
        },
    )
