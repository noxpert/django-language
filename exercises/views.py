import json
import random

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from vocabulary.models import Language, Translation, Word

from .utils import spelling_category, spelling_score


@login_required
@ensure_csrf_cookie
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
    same_language = False
    if source_language and target_language and source_language == target_language:
        same_language = True
    elif source_language and target_language:
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
        "same_language": same_language,
    }
    return render(request, "exercises/matching_exercise.html", context)


@login_required
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


@login_required
@ensure_csrf_cookie
def spelling_exercise(request):
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

    language_codes = list(languages.values_list("code", flat=True))
    if language_codes:
        if not source_language:
            source_language = language_codes[0]
        if not target_language:
            target_language = next(
                (code for code in language_codes if code != source_language),
                source_language,
            )

    word = None
    translation_word = None
    same_language = False
    if source_language and target_language and source_language == target_language:
        same_language = True
    elif source_language and target_language:
        last_word_id = request.session.get("spelling_last_word_id")
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
            translation_word = word.get_translation(target_language)
            if translation_word is None:
                word = None
            else:
                request.session["spelling_last_word_id"] = word.id

    context = {
        "languages": languages,
        "source_language": source_language,
        "target_language": target_language,
        "word": word,
        "translation_word": translation_word,
        "same_language": same_language,
    }
    return render(request, "exercises/spelling_exercise.html", context)


@login_required
@require_POST
def check_spelling(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid payload."}, status=400)

    word_id = payload.get("word_id")
    translation_id = payload.get("translation_id")
    answer = payload.get("answer", "")

    try:
        word_id = int(word_id)
        translation_id = int(translation_id)
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid word id."}, status=400)

    try:
        word = Word.objects.get(id=word_id)
    except Word.DoesNotExist:
        return JsonResponse({"success": False, "error": "Unknown word id."}, status=400)

    try:
        translation_word = Word.objects.get(id=translation_id)
    except Word.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Unknown translation id."}, status=400
        )

    is_valid = Translation.objects.filter(
        Q(source_word=word, target_word=translation_word)
        | Q(source_word=translation_word, target_word=word)
    ).exists()
    if not is_valid:
        return JsonResponse(
            {"success": False, "error": "Translation mismatch."}, status=400
        )

    use_vowel_pairs = translation_word.language.code == "hu"
    score = spelling_score(
        translation_word.word, answer, use_vowel_pairs=use_vowel_pairs
    )
    category = spelling_category(score)
    feedback = {
        "perfect": _("Correct!"),
        "almost": _("Almost!"),
        "partial": _("Keep trying!"),
        "wrong": _("Incorrect."),
    }[category]

    attempts_key = f"spelling_attempts_{word_id}"
    attempts = request.session.get(attempts_key, 0)
    correct_spelling = None
    if score == 100:
        request.session.pop(attempts_key, None)
    else:
        attempts += 1
        if attempts >= 3:
            correct_spelling = translation_word.word
            request.session.pop(attempts_key, None)
        else:
            request.session[attempts_key] = attempts

    return JsonResponse(
        {
            "success": True,
            "score": score,
            "category": category,
            "message": feedback,
            "word": word.word,
            "answer": answer,
            "correct_spelling": correct_spelling,
        }
    )
