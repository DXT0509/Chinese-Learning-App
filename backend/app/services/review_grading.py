"""Conservative lexical grading. No translation, tone folding or inferred senses."""

import re
import unicodedata

from app.core.pinyin import tone_marks


def hanzi(value: str) -> str:
    return unicodedata.normalize("NFC", value.strip())


def pinyin_matches(answer: str, numbered: str) -> bool:
    """Compare explicit syllables with a vetted identity, preserving every tone.

    Tone numbers delimit syllables. Marked text requires spaces/apostrophes;
    no speculative segmentation of unseparated multisyllable input is performed.
    A bare marked-format syllable denotes neutral tone, never a missing tone wildcard.
    """
    value = unicodedata.normalize("NFC", answer.strip().lower())
    value = value.replace("u:", "ü").replace("v", "ü").replace("’", "'")
    value = re.sub(r"[\s']+", " ", value)
    if any(c.isdigit() for c in value):
        # A numbered response must number every syllable, including neutral 5.
        tokens = re.findall(r"[a-züê]+[1-5]", value)
        if "".join(tokens) != value.replace(" ", ""):
            return False
        return " ".join(tokens) == numbered
    return value == tone_marks(numbered)


POS_OPTIONS = (
    "noun",
    "verb",
    "adjective",
    "adverb",
    "pronoun",
    "classifier",
    "numeral",
    "conjunction",
    "preposition",
    "particle",
    "interjection",
)


def grade(stage, answer, target):
    if stage == "HANZI":
        return isinstance(answer, str) and hanzi(answer) in target["accepted_simplified"]
    if stage == "PINYIN":
        return isinstance(answer, str) and any(
            pinyin_matches(answer, value) for value in target["accepted_pinyin_numbered"]
        )
    return (
        isinstance(answer, list)
        and len(answer) == len(set(answer))
        and set(answer) == set(target["accepted_pos"])
    )


def pinyin_mismatches(answer, numbered):
    """Only diagnose explicitly segmented numbered syllables, never guess segmentation."""
    if not isinstance(answer, str):
        return {}
    value = unicodedata.normalize("NFC", answer.strip().lower())
    value = value.replace("u:", "ü").replace("v", "ü").replace("’", "'")
    value = re.sub(r"[\s']+", " ", value)
    tokens = re.findall(r"[a-züê]+[1-5]", value)
    expected = numbered.split()
    if "".join(tokens) != value.replace(" ", "") or len(tokens) != len(expected):
        return {}
    tones, syllables = [], []
    for index, (actual, correct) in enumerate(zip(tokens, expected, strict=True), 1):
        if actual[:-1] != correct[:-1]:
            syllables.append(index)
        elif actual[-1] != correct[-1]:
            tones.append(index)
    return {"tone_mismatches": tones, "syllable_mismatches": syllables}
