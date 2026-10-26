import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import build_level_3
from generator_core import get_cumulative_state

batches = [
    (1, build_level_3.BATCH_001),
    (2, build_level_3.BATCH_002_CLEAN),
    (3, build_level_3.BATCH_003),
    (4, build_level_3.BATCH_004),
    (5, build_level_3.BATCH_005_CLEAN),
    (6, build_level_3.BATCH_006_CLEAN),
]

keys, existing_words, entries = get_cumulative_state()
seen_in_l3 = set()

for num, b in batches:
    lines = [l.strip() for l in b.strip().splitlines() if l.strip()]
    print(f"Batch {num} lines count: {len(lines)}")
    for i, l in enumerate(lines, 1):
        parts = l.split("|")
        if len(parts) != 9:
            print(f"  [ERROR] Batch {num} Line {i}: len={len(parts)} -> {l}")
        else:
            w = parts[0]
            if w in existing_words:
                print(f"  [DUP WITH L0-L2] Batch {num} Line {i}: {w}")
            if w in seen_in_l3:
                print(f"  [DUP IN L3] Batch {num} Line {i}: {w}")
            seen_in_l3.add(w)
