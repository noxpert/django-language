from django.db.models import Q
from django.shortcuts import render

from vocabulary.models import Language, Word


def random_word(request):
    languages = (
        Language.objects.filter(words__isnull=False)
        .filter(
            Q(words__translations_from__isnull=False)
            | Q(words__translations_to__isnull=False)
        )
        .distinct()
        .order_by("name")
    )

    source_language = request.GET.get("source_language")
    target_language = request.GET.get("target_language")
    word = None
    translation = None
    translation_definition = None
    same_language = False

    language_codes = list(languages.values_list("code", flat=True))
    if language_codes:
        if not source_language:
            source_language = language_codes[0]
        if not target_language:
            target_language = next(
                (code for code in language_codes if code != source_language),
                source_language,
            )

    if source_language and target_language and source_language == target_language:
        same_language = True
    elif source_language and target_language:
        last_word_id = request.session.get("wod_last_word_id")
        words = (
            Word.objects.filter(language__code=source_language)
            .filter(
                Q(translations_from__target_word__language__code=target_language)
                | Q(translations_to__source_word__language__code=target_language)
            )
            .exclude(id=last_word_id)
            .distinct()
            .order_by("?")[:1]
        )

        if not words and last_word_id:
            words = (
                Word.objects.filter(language__code=source_language)
                .filter(
                    Q(translations_from__target_word__language__code=target_language)
                    | Q(translations_to__source_word__language__code=target_language)
                )
                .distinct()
                .order_by("?")[:1]
            )

        if words:
            word = words[0]
            request.session["wod_last_word_id"] = word.id
            target_translation = word.get_translation(target_language)
            if target_translation:
                translation = target_translation.word
                translation_definition = target_translation.definition
            else:
                translation = ""

    return render(
        request,
        "wod/random_word.html",
        {
            "word": word,
            "translation": translation,
            "translation_definition": translation_definition,
            "languages": languages,
            "source_language": source_language,
            "target_language": target_language,
            "same_language": same_language,
        },
    )
