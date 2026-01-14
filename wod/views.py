from django.shortcuts import render

from .models import Language, Word


def random_word(request):
    languages = Language.objects.filter(word__isnull=False).distinct()
    selected_language = request.GET.get("language")

    words = Word.objects.all()
    if selected_language:
        words = words.filter(language__code=selected_language)

    word = words.order_by("?").first()

    return render(
        request,
        "wod/random_word.html",
        {"word": word, "languages": languages, "selected_language": selected_language},
    )
