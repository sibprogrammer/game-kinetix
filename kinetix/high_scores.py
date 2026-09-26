HIGH_SCORE_COUNT = 10


def top(scores=()):
    if any(not isinstance(score, int) or score < 0 for score in scores):
        raise ValueError("scores must be nonnegative integers")
    return sorted([*scores, *([0] * HIGH_SCORE_COUNT)], reverse=True)[
        :HIGH_SCORE_COUNT
    ]


def record(score, scores=()):
    if score < 0:
        raise ValueError("score must not be negative")
    return top([*scores, score])
