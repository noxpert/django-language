import pytest

from exercises.utils import spelling_category, spelling_score


@pytest.mark.parametrize(
    ("expected", "actual", "score", "category"),
    [
        ("book", "book", 100, "perfect"),
        ("alma", "álma", 95, "almost"),
        ("ball", "bal", 95, "almost"),
        ("bal", "ball", 95, "almost"),
        ("boat", "bot", 90, "partial"),
        ("cat", "cart", 90, "partial"),
        ("right", "riggt", 90, "partial"),
        ("apple", "apxle", 90, "partial"),
        ("family", "famíli", 85, "partial"),
        ("abcd", "efgh", 60, "wrong"),
    ],
)
def test_spelling_score(expected, actual, score, category):
    assert spelling_score(expected, actual) == score
    assert spelling_category(score) == category


def test_spelling_score_skips_vowel_pairs_when_disabled():
    assert spelling_score("alma", "álma", use_vowel_pairs=False) == 90
