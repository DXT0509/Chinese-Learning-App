"""Versioned two-stage projections of already validated editorial sense policies."""

import hashlib
import json
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TwoStagePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_version: Literal[2] = 2
    policy_version: Literal["handwriting-pinyin-v2"] = "handwriting-pinyin-v2"
    source_policy_version: str
    source_snapshot_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    vocabulary_id: str
    content_version: int = Field(ge=1)
    checksum: str
    sense_key: str
    vietnamese_prompt: str
    accepted_simplified: list[str] = Field(min_length=1)
    accepted_pinyin_numbered: list[str] = Field(min_length=1)
    applicable_stages: tuple[Literal["HANZI"], Literal["PINYIN"]] = ("HANZI", "PINYIN")


def project(target):
    snapshot = target.snapshot()
    # Retain sense/cue wording; the old instruction for a removed stage is obsolete.
    prompt = re.sub(r"\s*Ở bước từ loại,.*$", "", snapshot["vietnamese_prompt"] or "")
    policy = TwoStagePolicy(
        source_policy_version=snapshot["policy_version"] or "unavailable",
        source_snapshot_sha256=hashlib.sha256(
            json.dumps(snapshot, sort_keys=True).encode()
        ).hexdigest(),
        vocabulary_id=snapshot["vocabulary_id"],
        content_version=snapshot["content_version"],
        checksum=snapshot["checksum"],
        sense_key=snapshot["sense_key"] or "unavailable",
        vietnamese_prompt=prompt,
        accepted_simplified=list(snapshot["accepted_simplified"]),
        accepted_pinyin_numbered=list(snapshot["accepted_pinyin_numbered"]),
    )
    return {
        **snapshot,
        **policy.model_dump(mode="json"),
        "review_version": "two-stage-v2",
        "disabled_stages": [],
        "accepted_pos": [],
        "pos_options": [],
        "pos_prompt_vi": None,
    }
