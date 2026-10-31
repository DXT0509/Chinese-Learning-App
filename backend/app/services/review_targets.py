"""Strict operator-authored, version-bound sense policies; no automatic ambiguity guesses."""

import re
from collections import defaultdict
from uuid import UUID

from pydantic import Field, model_serializer, model_validator
from sqlalchemy import select

from app.core.pinyin import tone_marks
from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.models.curated_vocabulary import VocabularyMeaning
from app.models.srs import SrsTargetPolicy
from app.schemas.curated_vocabulary import StrictRecord, Text, is_hanzi, simplified_only
from app.services.contextual_grammar import POLICY_VERSION, ContextualGrammar
from app.services.review_grading import POS_OPTIONS
from app.services.srs_contract import ReviewTarget, Stage


class ReviewedPolicy(StrictRecord):
    vocabulary_id: UUID
    content_version: int = Field(ge=1, strict=True)
    checksum: str = Field(pattern=r"^[a-f0-9]{64}$")
    policy_version: Text
    sense_key: Text
    vietnamese_prompt: Text
    reviewed_by: Text
    ambiguity_resolution: Text
    accepted_pos: list[str] = Field(default_factory=list, max_length=11)
    pos_skip_reason: Text | None = None
    grammatical_review: ContextualGrammar | None = None

    @model_serializer(mode="wrap")
    def preserve_legacy_payload(self, handler):
        payload = handler(self)
        if self.grammatical_review is None:
            payload.pop("grammatical_review", None)
        return payload

    @model_validator(mode="after")
    def supported_policy(self):
        if any(is_hanzi(c) for c in self.vietnamese_prompt):
            raise ValueError("Vietnamese prompt must not contain a Chinese answer")
        options = self.grammatical_review.options if self.grammatical_review else POS_OPTIONS
        if len(self.accepted_pos) != len(set(self.accepted_pos)) or any(
            value not in options for value in self.accepted_pos
        ):
            raise ValueError("Use distinct supported POS categories")
        if bool(self.accepted_pos) == bool(self.pos_skip_reason):
            raise ValueError("Specify reviewed POS or an explicit skip reason")
        if self.grammatical_review and (
            self.policy_version != POLICY_VERSION or not self.accepted_pos or self.pos_skip_reason
        ):
            raise ValueError("Contextual grammar must retain an assessed third stage")
        if self.policy_version == POLICY_VERSION and not self.grammatical_review:
            raise ValueError("Contextual grammar policy requires recorded review evidence")
        return self

    def target(self, word):
        if (self.vocabulary_id, self.content_version, self.checksum) != (
            word.id,
            word.content_version,
            word.checksum,
        ):
            raise ValueError("Stale policy identity")
        # All selected categories must have actual catalog support. The operator
        # supplies sense selection; delimiter order never implies sense alignment.
        raw = set(re.split(r"\s*[;,/]\s*", (word.part_of_speech or "").lower()))
        raw = {"classifier" if value == "measure word" else value for value in raw}
        if self.policy_version == "catalog-context-v2":
            from app.services.policy_coverage import catalog_pos

            supported, unknown = catalog_pos(word.part_of_speech)
            if unknown:
                raise ValueError("Unsupported source POS requires editorial review")
            raw = set(supported)
        if self.grammatical_review:
            self.grammatical_review.validate_word(word)
        elif not set(self.accepted_pos) <= raw:
            raise ValueError("Selected POS lacks catalog support")
        if not word.simplified or not word.pinyin_numbered:
            raise ValueError("Missing lexical identity")
        simplified_only(word.simplified)
        if (
            not all(is_hanzi(c) for c in word.simplified)
            or not re.fullmatch(r"[a-zü]+[1-5](?: [a-zü]+[1-5])*", word.pinyin_numbered)
            or len(word.pinyin_numbered.split()) != len(word.simplified)
            or word.lexical_key != f"{word.simplified}|{word.pinyin_numbered}"
            or tone_marks(word.pinyin_numbered) != word.pinyin
        ):
            raise ValueError("Non-gradable lexical identity")
        return ReviewTarget(
            word.id,
            word.lexical_key,
            word.content_version,
            word.checksum,
            applicable_stages=(Stage.HANZI, Stage.PINYIN, Stage.POS)
            if self.accepted_pos
            else (Stage.HANZI, Stage.PINYIN),
            disabled_stages=() if self.accepted_pos else ((Stage.POS, self.pos_skip_reason),),
            policy_version=self.policy_version,
            sense_key=self.sense_key,
            vietnamese_prompt=self.vietnamese_prompt,
            accepted_simplified=(word.simplified,),
            accepted_pinyin_numbered=(word.pinyin_numbered,),
            accepted_pos=tuple(self.accepted_pos),
            pos_prompt_vi=self.grammatical_review.prompt(word) if self.grammatical_review else None,
            pos_options=self.grammatical_review.options if self.grammatical_review else (),
        )


class ReviewedTargets:
    async def resolve(self, session, word):
        policy = await session.get(SrsTargetPolicy, (word.id, word.content_version, word.checksum))
        if policy:
            try:
                target = ReviewedPolicy.model_validate(policy.policy).target(word)
                meaning = await session.scalar(
                    select(VocabularyMeaning.gloss)
                    .where(
                        VocabularyMeaning.vocabulary_id == word.id,
                        VocabularyMeaning.language == "vi",
                    )
                    .limit(1)
                )
                if meaning and meaning.strip():
                    reviewed = ReviewedPolicy.model_validate(policy.policy)
                    if reviewed.grammatical_review:
                        from app.models.curated_vocabulary import VocabularyExample

                        supported = await session.scalar(
                            select(VocabularyExample.vocabulary_id)
                            .where(
                                VocabularyExample.vocabulary_id == word.id,
                                VocabularyExample.simplified
                                == reviewed.grammatical_review.source_example,
                            )
                            .limit(1)
                        )
                        if supported is None:
                            return ReviewTarget(
                                word.id, word.lexical_key, word.content_version, word.checksum
                            )
                    if target.policy_version in ("catalog-cued-v1", "catalog-context-v2"):
                        # Lazy import: preparation reuses the strict policy contract.
                        from app.services.policy_preparation import catalog_entries, prepare

                        # Per-transaction cache only; never retain publication/collision
                        # decisions across requests or content changes.
                        transaction = session.sync_session.get_transaction()
                        cached = session.info.get("review_catalog_entries")
                        if cached is None or cached[0] is not transaction:
                            cached = (transaction, await catalog_entries(session), {})
                            session.info["review_catalog_entries"] = cached
                        # All catalog rows still participate in collision/publication checks.
                        # Generate only the requested identity, not thousands of unrelated policies.
                        identity = (target.policy_version, word.id)
                        if identity not in cached[2]:
                            batch = session.info.get("review_policy_batch")
                            requested = batch[1] if batch and batch[0] is transaction else {word.id}
                            requested = requested | {word.id}
                            if target.policy_version == "catalog-context-v2":
                                from app.services.policy_coverage import prepare_coverage

                                prepared, _ = prepare_coverage(cached[1], only_ids=requested)
                            else:
                                prepared, _ = prepare(cached[1], only_ids=requested)
                            generated = {p.vocabulary_id: p for p in prepared}
                            for identifier in requested:
                                cached[2][(target.policy_version, identifier)] = generated.get(
                                    identifier
                                )
                        if cached[2][identity] != ReviewedPolicy.model_validate(policy.policy):
                            return ReviewTarget(
                                word.id, word.lexical_key, word.content_version, word.checksum
                            )
                    return target
            except ValueError:
                pass
        return ReviewTarget(word.id, word.lexical_key, word.content_version, word.checksum)


async def editorial_flags(session, words):
    """Candidates for editorial attention, never automatic sense/answer approval."""
    meanings, gloss_ids, forms = defaultdict(list), defaultdict(set), defaultdict(set)
    for identifier, gloss in await session.execute(
        select(VocabularyMeaning.vocabulary_id, VocabularyMeaning.gloss).where(
            VocabularyMeaning.language == "vi"
        )
    ):
        meanings[identifier].append(gloss)
        gloss_ids[gloss.strip().casefold()].add(identifier)
    for identifier, form in await session.execute(select(Word.id, Word.simplified)):
        forms[form].add(identifier)
    flags = {}
    for word in words:
        issues = []
        if not meanings[word.id]:
            issues.append("MISSING_VIETNAMESE_MEANING")
        if len(meanings[word.id]) > 1:
            issues.append("MULTIPLE_MEANINGS_REQUIRE_SENSE_REVIEW")
        if any(len(gloss_ids[g.strip().casefold()]) > 1 for g in meanings[word.id]):
            issues.append("SHARED_VIETNAMESE_GLOSS")
        if len(forms[word.simplified]) > 1:
            issues.append("MULTIPLE_PRONUNCIATION_IDENTITIES")
        if not word.part_of_speech:
            issues.append("MISSING_POS")
        elif any(c in word.part_of_speech for c in ";,/|"):
            issues.append("MULTIPLE_OR_COMPOUND_POS")
        flags[word.id] = issues
    return flags
