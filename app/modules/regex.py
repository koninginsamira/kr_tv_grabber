from re import Pattern, search


def find_first(pattern: str | Pattern[str], string: str) -> str | None:
    return (match := search(pattern, string)) and match.group(0) or None