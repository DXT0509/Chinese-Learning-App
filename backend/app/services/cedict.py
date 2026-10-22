"""Strict CC-CEDICT v1 parsing. No network acquisition or inferred translations."""

import gzip
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from uuid import UUID, uuid5

SOURCE = "cc-cedict"
SOURCE_URL = "https://www.mdbg.net/chinese/dictionary?page=cedict"
LICENSE = "CC-BY-SA-4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
ATTRIBUTION = "CC-CEDICT contributors; provided by MDBG."
CHANGES = "NFC normalization; numbered pinyin rendered with tone marks; ordered English glosses."
NAMESPACE = UUID("8948b27f-0b85-46a8-99bc-6f35d96799f6")
ROW = re.compile(r"^(\S+) (\S+) \[([^\[\]]+)\] /(.+)/$")
SYLLABLE = re.compile(r"([A-Za-züÜêÊ:]+)([1-5])")


class DictionaryImportError(ValueError):
    """Safe diagnostic: never includes original row content or database values."""


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
            raise DictionaryImportError("Unrenderable pinyin syllable")
        mark = ("\u0304", "\u0301", "\u030c", "\u0300")[tone - 1]
        return unicodedata.normalize(
            "NFC", letters[: position + 1] + mark + letters[position + 1 :]
        )

    return SYLLABLE.sub(convert, numbered)


@dataclass(frozen=True)
class CedictEntry:
    id: UUID
    traditional: str
    simplified: str
    pinyin_numbered: str
    pinyin: str
    english_glosses: list[str]


@dataclass(frozen=True)
class CedictDataset:
    sha256: str
    entries: list[CedictEntry]
    duplicate_rows: int


def parse_row(line: str) -> CedictEntry:
    match = ROW.fullmatch(unicodedata.normalize("NFC", line.strip()))
    if not match:
        raise DictionaryImportError("Invalid v1 row")
    traditional, simplified, pinyin, glosses = match.groups()
    pinyin = " ".join(pinyin.split())
    senses = glosses.split("/")
    if (
        max(len(traditional), len(simplified)) > 255
        or len(pinyin) > 500
        or not all(s.strip() for s in senses)
        or any(unicodedata.category(c).startswith("C") for c in line.strip())
    ):
        raise DictionaryImportError("Invalid v1 fields")
    # Identity excludes mutable definitions and revision, preserves case/pronunciation.
    identity = json.dumps([SOURCE, traditional, simplified, pinyin], ensure_ascii=False)
    return CedictEntry(
        uuid5(NAMESPACE, identity),
        traditional,
        simplified,
        pinyin,
        tone_marks(pinyin),
        senses,
    )


def load_dataset(path: Path, expected_sha256: str) -> CedictDataset:
    # Parse exactly the bytes whose checksum was verified, even if the path is replaced.
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256) or actual != expected_sha256:
        raise DictionaryImportError("Source SHA-256 mismatch")
    if path.suffix == ".gz":
        payload = gzip.decompress(payload)
    entries = {}
    malformed = []
    duplicates = 0
    with StringIO(payload.decode("utf-8-sig")) as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                entry = parse_row(line)
                previous = entries.get(entry.id)
                if previous and previous != entry:
                    raise DictionaryImportError("Conflicting lexical key")
                duplicates += int(previous is not None)
                entries[entry.id] = entry
            except DictionaryImportError:
                malformed.append(number)
    if malformed:
        locations = ", ".join(map(str, malformed[:20]))
        raise DictionaryImportError(
            f"Malformed/conflicting rows: {len(malformed)}; lines {locations}"
        )
    if not entries:
        raise DictionaryImportError("Dataset contains no entries")
    return CedictDataset(actual, list(entries.values()), duplicates)
