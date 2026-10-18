"""Replaceable object interface and immutable local content-addressed adapter."""

import hashlib
import os
import re
import tempfile
from pathlib import Path
from typing import Protocol

from app.services.content_files import ContentError


class ContentStorage(Protocol):
    def read(self, key: str) -> bytes: ...
    def put_bundle(self, data: bytes) -> str: ...


class LocalContentStorage:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def _path(self, key: str) -> Path:
        if not re.fullmatch(r"sha256/[0-9a-f]{64}\.[a-z0-9]+", key):
            raise ContentError("invalid stable object key")
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root):
            raise ContentError("object key escapes storage directory")
        return path

    def read(self, key: str) -> bytes:
        try:
            path = self._path(key)
            if path.stat().st_size > 50_000_000:
                raise ContentError("object exceeds 50 MB")
            return path.read_bytes()
        except OSError:
            raise ContentError("referenced object is missing or unreadable") from None

    def put_bundle(self, data: bytes) -> str:
        digest = hashlib.sha256(data).hexdigest()
        key = f"sha256/{digest}.json"
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        # A complete temporary object is linked into place without replacing any existing file.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, path)
            except FileExistsError:
                if self.read(key) != data:
                    raise ContentError("existing content-addressed object is corrupt") from None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return key


def verify_object(storage: ContentStorage, key: str, digest: str, length: int) -> bytes:
    data = storage.read(key)
    if len(data) != length or hashlib.sha256(data).hexdigest() != digest:
        raise ContentError("object length or SHA-256 does not match asset metadata")
    return data
