import json
import random

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from vocabulary.models import Language, Word


def matching_exercise(request):
    languages = Language.objects.filter(word__isnull=False).distinct()
    selected_language = request.GET.get("language")
    count_param = request.GET.get("count", "5")

    try:
        count = int(count_param)
    except (TypeError, ValueError):
        count = 5

    count = max(2, min(10, count))

    words = []
    translations = []
    if selected_language:
        words = list(
            Word.objects.filter(language__code=selected_language).order_by("?")[:count]
        )
        translations = [word.translation for word in words]
        random.shuffle(translations)

    context = {
        "languages": languages,
        "selected_language": selected_language,
        "count": count,
        "count_options": list(range(2, 11)),
        "words": words,
        "translations": translations,
    }
    return render(request, "matching/exercise.html", context)


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

    words = Word.objects.filter(id__in=word_ids)
    if words.count() != len(word_ids):
        return JsonResponse({"success": False, "error": "Unknown word id."}, status=400)

    words_by_id = {str(word.id): word for word in words}
    results = []
    score = 0

    for word_id, chosen_translation in matches.items():
        word = words_by_id[word_id]
        is_correct = word.translation == chosen_translation
        if is_correct:
            score += 1
        results.append(
            {
                "word_id": word_id,
                "word": word.word,
                "correct_translation": word.translation,
                "chosen_translation": chosen_translation,
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
