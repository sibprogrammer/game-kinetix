from pathlib import Path

HIGH_SCORE_COUNT = 10
DEFAULT_FILE_PATH = Path(__file__).parent.parent / "scores"


def top(file_path=DEFAULT_FILE_PATH):
    file_path = Path(file_path)
    if not file_path.exists():
        return [0] * HIGH_SCORE_COUNT

    scores = []
    for line_number, line in enumerate(file_path.read_text().splitlines(), start=1):
        try:
            score = int(line)
        except ValueError as error:
            raise ValueError(
                f"invalid score on line {line_number} of {file_path}"
            ) from error
        if score < 0:
            raise ValueError(f"negative score on line {line_number} of {file_path}")
        scores.append(score)

    return sorted(scores + [0] * HIGH_SCORE_COUNT, reverse=True)[:HIGH_SCORE_COUNT]


def record(score, file_path=DEFAULT_FILE_PATH):
    if score < 0:
        raise ValueError("score must not be negative")

    file_path = Path(file_path)
    scores = sorted(top(file_path) + [score], reverse=True)[:HIGH_SCORE_COUNT]
    file_path.write_text("\n".join(map(str, scores)) + "\n")
    return scores
