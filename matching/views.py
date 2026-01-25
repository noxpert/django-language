import json
import random

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from vocabulary.models import Language, Translation, Word


def matching_exercise(request):
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
    count_param = request.GET.get("count", "5")

    try:
        count = int(count_param)
    except (TypeError, ValueError):
        count = 5

    count = max(2, min(10, count))

    language_codes = list(languages.values_list("code", flat=True))
    if language_codes:
        if not source_language:
            source_language = language_codes[0]
        if not target_language:
            target_language = next(
                (code for code in language_codes if code != source_language),
                source_language,
            )

    words = []
    translations = []
    if source_language and target_language:
        word_queryset = (
            Word.objects.filter(language__code=source_language)
            .filter(
                Q(translations_from__target_word__language__code=target_language)
                | Q(translations_to__source_word__language__code=target_language)
            )
            .distinct()
        )
        candidate_words = list(word_queryset.order_by("?")[:count])
        for word in candidate_words:
            options = word.get_translations(target_language)
            if not options:
                continue
            words.append(word)
            translations.append(random.choice(options))
        random.shuffle(translations)

    context = {
        "languages": languages,
        "source_language": source_language,
        "target_language": target_language,
        "count": count,
        "count_options": list(range(2, 11)),
        "words": words,
        "translations": translations,
    }
    return render(request, "matching/matching_exercise.html", context)


@require_POST
def check_matches(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid payload."}, status=400)

    matches = payload.get("matches", {})
    if not isinstance(matches, dict):
        return JsonResponse({"success": False, "error": "Invalid matches."}, status=400)

    if not matches:
        return JsonResponse({"success": True, "results": [], "score": 0, "total": 0})

    try:
        word_ids = [int(word_id) for word_id in matches.keys()]
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid word id."}, status=400)

    try:
        translation_ids = [int(translation_id) for translation_id in matches.values()]
    except (TypeError, ValueError):
        return JsonResponse(
            {"success": False, "error": "Invalid translation id."}, status=400
        )

    words = Word.objects.filter(id__in=word_ids)
    if words.count() != len(word_ids):
        return JsonResponse({"success": False, "error": "Unknown word id."}, status=400)

    unique_translation_ids = set(translation_ids)
    translations = Word.objects.filter(id__in=unique_translation_ids)
    if translations.count() != len(unique_translation_ids):
        return JsonResponse(
            {"success": False, "error": "Unknown translation id."}, status=400
        )

    words_by_id = {str(word.id): word for word in words}
    translations_by_id = {str(word.id): word for word in translations}
    results = []
    score = 0

    for word_id, chosen_translation_id in matches.items():
        word = words_by_id[word_id]
        chosen_translation = translations_by_id.get(str(chosen_translation_id))
        if chosen_translation is None:
            return JsonResponse(
                {"success": False, "error": "Unknown translation id."}, status=400
            )

        is_correct = Translation.objects.filter(
            Q(source_word=word, target_word=chosen_translation)
            | Q(source_word=chosen_translation, target_word=word)
        ).exists()
        correct_translation = word.get_translation(
            chosen_translation.language.code
        ) or next(iter(word.get_translations()), None)
        correct_translation_text = (
            correct_translation.word if correct_translation else ""
        )
        if is_correct:
            score += 1
        results.append(
            {
                "word_id": word_id,
                "word": word.word,
                "correct_translation": correct_translation_text,
                "chosen_translation": chosen_translation.word,
                "is_correct": is_correct,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "results": results,
            "score": score,
            "total": len(results),
        }
    )
