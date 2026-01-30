VOWEL_PAIRS = {
    "a": "á",
    "á": "a",
    "e": "é",
    "é": "e",
    "i": "í",
    "í": "i",
    "o": "ó",
    "ó": "o",
    "ö": "ő",
    "ő": "ö",
    "u": "ú",
    "ú": "u",
    "ü": "ű",
    "ű": "ü",
}


def normalize_spelling(value):
    return value.strip().lower()


def _single_mismatch_score(expected, actual, use_vowels):
    if len(expected) != len(actual):
        return None
    mismatches = [idx for idx, char in enumerate(expected) if char != actual[idx]]
    if len(mismatches) != 1:
        return None
    index = mismatches[0]
    if use_vowels and VOWEL_PAIRS.get(expected[index]) == actual[index]:
        return 95
    return 90


def _delete_cost(expected, index):
    if index >= 2 and expected[index - 1] == expected[index - 2]:
        return 5
    if index < len(expected) and expected[index - 1] == expected[index]:
        return 5
    return 10


def _insert_cost(actual, index):
    if index >= 2 and actual[index - 1] == actual[index - 2]:
        return 5
    if index < len(actual) and actual[index - 1] == actual[index]:
        return 5
    return 10


def _substitute_cost(expected_char, actual_char, use_vowels):
    if use_vowels and VOWEL_PAIRS.get(expected_char) == actual_char:
        return 5
    return 10


def spelling_score(expected, actual, *, use_vowel_pairs=True):
    expected = normalize_spelling(expected)
    actual = normalize_spelling(actual)

    if expected == actual:
        return 100

    single_mismatch = _single_mismatch_score(expected, actual, use_vowel_pairs)
    if single_mismatch is not None:
        return single_mismatch

    rows = len(expected) + 1
    cols = len(actual) + 1
    matrix = [[0] * cols for _ in range(rows)]

    for i in range(1, rows):
        matrix[i][0] = matrix[i - 1][0] + _delete_cost(expected, i)
    for j in range(1, cols):
        matrix[0][j] = matrix[0][j - 1] + _insert_cost(actual, j)

    for i in range(1, rows):
        for j in range(1, cols):
            delete_cost = matrix[i - 1][j] + _delete_cost(expected, i)
            insert_cost = matrix[i][j - 1] + _insert_cost(actual, j)
            substitute_cost = matrix[i - 1][j - 1]
            if expected[i - 1] != actual[j - 1]:
                substitute_cost += _substitute_cost(
                    expected[i - 1], actual[j - 1], use_vowel_pairs
                )
            matrix[i][j] = min(delete_cost, insert_cost, substitute_cost)

    score = 100 - matrix[-1][-1]
    return max(0, score)


def spelling_category(score):
    if score >= 100:
        return "perfect"
    if score == 95:
        return "almost"
    if score >= 75:
        return "partial"
    return "wrong"
