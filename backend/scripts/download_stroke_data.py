"""Download stroke vector data from Make Me a Hanzi / hanzi-writer-data into assets/strokes/<unicode-hex>.json.

Usage:
    python backend/scripts/download_stroke_data.py [--all]
"""

import argparse
import glob
import json
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "https://raw.githubusercontent.com/chanind/hanzi-writer-data/master/data/{char}.json"

def get_lesson_characters(all_datasets: bool = False) -> set[str]:
    chars = set()

    # Always scan hsk-0-pack and test files
    for p in glob.glob("backend/content/roadmaps/preparation/hsk-0-pack/**/*.json", recursive=True):
        try:
            with open(p, "r", encoding="utf-8") as f:
                for c in f.read():
                    if "\u4e00" <= c <= "\u9fff":
                        chars.add(c)
        except Exception:
            pass

    test_files = [
        "android/app/src/test/java/com/example/chineselearningapp/RoadmapTest.kt",
        "android/app/src/androidTest/java/com/example/chineselearningapp/LessonFlowUiTest.kt",
        "android/app/src/androidTest/java/com/example/chineselearningapp/RoadmapUiTest.kt",
        "backend/scripts/deploy_hsk0_v4.py",
        "backend/scripts/finalize_hsk0_review.py",
    ]
    for p in test_files:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for c in f.read():
                    if "\u4e00" <= c <= "\u9fff":
                        chars.add(c)

    # If all_datasets requested or by default include common lesson batches
    if all_datasets:
        for p in glob.glob("docs/datasets/**/*.json", recursive=True) + glob.glob("docs/datasets/**/*.jsonl", recursive=True):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        for c in line:
                            if "\u4e00" <= c <= "\u9fff":
                                chars.add(c)
            except Exception:
                pass
    else:
        # Include level-0 batch
        for p in glob.glob("docs/datasets/original-zhvi/level-0*.jsonl"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        for c in line:
                            if "\u4e00" <= c <= "\u9fff":
                                chars.add(c)
            except Exception:
                pass

    return chars

def download_character(char: str, out_dir: Path) -> bool:
    hex_code = f"{ord(char):04x}"
    out_file = out_dir / f"{hex_code}.json"
    if out_file.exists():
        return True

    url = BASE_URL.format(char=urllib.parse.quote(char))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ChineseLearningApp-StrokeDownloader/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            # Keep only strokes and medians to save space
            compact = {
                "strokes": data.get("strokes", []),
                "medians": data.get("medians", [])
            }
            out_file.write_text(json.dumps(compact, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
            return True
    except Exception as e:
        print(f"Failed to download {char} ({hex_code}): {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download stroke vector data")
    parser.add_argument("--all", action="store_true", help="Download for all characters across all datasets")
    parser.add_argument("--chars", type=str, help="Specific characters to download")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent
    out_dir = project_root / "android/app/src/main/assets/strokes"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.chars:
        chars = set(args.chars)
    else:
        chars = get_lesson_characters(all_datasets=args.all)

    print(f"Target characters count: {len(chars)}")
    success_count = 0
    fail_count = 0
    for i, ch in enumerate(sorted(chars), 1):
        if download_character(ch, out_dir):
            success_count += 1
        else:
            fail_count += 1
        if i % 20 == 0 or i == len(chars):
            print(f"Progress: {i}/{len(chars)} (Success: {success_count}, Fail: {fail_count})")

    print(f"Completed: {success_count} downloaded / existing, {fail_count} failed.")

if __name__ == "__main__":
    main()

