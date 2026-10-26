"""Provider-independent numbered Pinyin rendering."""

import re
import unicodedata

SYLLABLE = re.compile(r"([A-Za-züÜêÊ:]+)([1-5])")


def tone_marks(numbered: str) -> str:
    def convert(match):
        letters = match[1].replace("u:", "ü").replace("U:", "Ü")
        tone = int(match[2])
        if tone == 5:
            return letters
        lower = letters.lower()
        if "a" in lower:
            position = lower.index("a")
        elif "e" in lower or "ê" in lower:
            position = next(i for i, c in enumerate(lower) if c in "eê")
        elif "ou" in lower:
            position = lower.index("o")
        else:
            vowels = [i for i, c in enumerate(lower) if c in "iouü"]
            # Syllabic m/n occur in the source too.
            position = (
                vowels[-1] if vowels else next((i for i, c in enumerate(lower) if c in "mn"), -1)
            )
        if position < 0:
            raise ValueError("Unrenderable pinyin syllable")
        mark = ("\u0304", "\u0301", "\u030c", "\u0300")[tone - 1]
        return unicodedata.normalize(
            "NFC", letters[: position + 1] + mark + letters[position + 1 :]
        )

    return SYLLABLE.sub(convert, numbered)
