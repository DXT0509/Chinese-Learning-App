"""Fetch six explicitly licensed Commons originals; no TTS, account or database writes."""

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

from app.services.content_files import ContentError
from app.services.roadmap_preparation import load_json, write_artifact

SOURCES = [
    ("wo", "Zh-wǒ.ogg", "https://creativecommons.org/licenses/by/2.0/fr/"),
    ("ni", "Zh-nǐ.ogg", "https://creativecommons.org/licenses/by/2.0/fr/"),
    ("hao", "Zh-hǎo.ogg", "https://creativecommons.org/licenses/by/2.0/fr/"),
    ("wo", "我-order.gif", "https://creativecommons.org/licenses/by/3.0/"),
    ("ni", "你-order.gif", "https://creativecommons.org/licenses/by/3.0/"),
    ("hao", "好-order.gif", "https://creativecommons.org/licenses/by/3.0/"),
]


def fetch(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {
        "commons.wikimedia.org",
        "upload.wikimedia.org",
    }:
        raise ContentError("only the reviewed Wikimedia HTTPS hosts are allowed")
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ChineseLearningApp-HSK0Preparation/1.0 (local educational asset preparation)",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(1_000_001)
    if len(data) > 1_000_000:
        raise ContentError("unexpected asset/metadata size")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt_path = args.output / "sources.json"
    if receipt_path.exists():
        for row in load_json(receipt_path):
            raw = (args.output / row["file"]).read_bytes()
            if hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise ContentError(
                    "existing source asset differs; do not overwrite immutable sources"
                )
        print("Six pinned originals already verified; no download needed")
        return
    receipts = []
    for stem, title, license_url in SOURCES:
        suffix = ".ogg" if title.endswith(".ogg") else ".gif"
        filename = stem + suffix
        checkpoint = args.output / f"{filename}.source.json"
        if checkpoint.exists():
            row = load_json(checkpoint)
            if hashlib.sha256((args.output / filename).read_bytes()).hexdigest() != row["sha256"]:
                raise ContentError("checkpoint integrity mismatch")
            receipts.append(row)
            continue
        query = urllib.parse.urlencode(
            {
                "action": "query",
                "format": "json",
                "prop": "imageinfo",
                "titles": f"File:{title}",
                "iiprop": "url|sha1|size|mime|extmetadata|timestamp|user",
            }
        )
        pages = json.loads(fetch(f"https://commons.wikimedia.org/w/api.php?{query}"))["query"][
            "pages"
        ]
        info = next(iter(pages.values()))["imageinfo"][0]
        meta = info["extmetadata"]
        actual_license = meta.get("LicenseUrl", {}).get("value", "").replace("http:", "https:")
        if actual_license.removesuffix("deed.en").rstrip("/") != license_url.rstrip("/"):
            raise ContentError(f"{title}: source license differs from reviewed license; stop")
        destination = args.output / filename
        raw = destination.read_bytes() if destination.exists() else fetch(info["url"])
        if hashlib.sha1(raw).hexdigest() != info["sha1"] or len(raw) != info["size"]:
            raise ContentError(f"{title}: upstream integrity mismatch")
        args.output.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.read_bytes() != raw:
            raise ContentError("refusing to replace a previously downloaded source asset")
        destination.write_bytes(raw)
        row = {
            "title": title,
            "file": filename,
            "source": info["descriptionurl"],
            "download": info["url"],
            "upstream_timestamp": info["timestamp"],
            "upstream_sha1": info["sha1"],
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_length": len(raw),
            "media_type": "audio/ogg" if suffix == ".ogg" else "image/gif",
            "license_url": license_url,
            "author_html": meta.get("Artist", {}).get("value"),
            "credit_html": meta.get("Credit", {}).get("value"),
            "changes": "None; original bytes",
            "educational_review": "PENDING",
            "human_approval": None,
        }
        write_artifact(checkpoint, row, immutable=True)
        receipts.append(row)
        print(f"Prepared {filename}: {len(raw)} original bytes")
    write_artifact(receipt_path, receipts, immutable=True)


if __name__ == "__main__":
    main()
