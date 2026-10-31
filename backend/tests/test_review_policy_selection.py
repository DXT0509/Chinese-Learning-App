"""Target-only preparation must retain the complete catalog safety boundary."""

from copy import deepcopy

import pytest

from app.services.policy_coverage import prepare_coverage
from app.services.policy_preparation import prepare
from tests.test_curated_vocabulary import curated_sessions as curated_sessions  # noqa: PLC0414
from tests.test_policy_preparation import entry


@pytest.mark.parametrize("generate", [prepare, prepare_coverage])
@pytest.mark.parametrize("collision", ["none", "form", "cue", "hidden_peer", "overlap"])
def test_selected_policy_equals_full_preparation_and_keeps_all_peers(generate, collision):
    target = entry()
    other = entry(
        simplified="马",
        pinyin="mǎ",
        pinyin_numbered="ma3",
        lexical_key="马|ma3",
        sino_vietnamese="mã",
        part_of_speech="noun",
    )
    other.meanings = ["con ngựa"]
    if collision == "form":
        other.word.simplified = target.word.simplified
        other.word.lexical_key = "学|ma3"
    elif collision in ("cue", "hidden_peer", "overlap"):
        other.word.sino_vietnamese = target.word.sino_vietnamese
        other.meanings = list(target.meanings)
        if collision == "hidden_peer":
            other.published = False
        if collision == "overlap":
            other.meanings.append("nghiên cứu")
    entries = [target, other]
    full, _ = generate(entries)
    before = deepcopy([(e.word.checksum, e.meanings, e.published) for e in entries])
    for selected in entries:
        actual, _ = generate(entries, only_ids={selected.word.id})
        assert actual == [p for p in full if p.vocabulary_id == selected.word.id]
    assert before == [(e.word.checksum, e.meanings, e.published) for e in entries]
    assert generate(entries, only_ids=set())[0] == []
    if collision in ("form", "cue", "hidden_peer", "overlap"):
        assert generate([target], only_ids={target.word.id})[0]
        assert not generate(entries, only_ids={target.word.id})[0]


@pytest.mark.postgres
async def test_batch_generation_is_shared_and_transaction_scope_is_not_reused(
    curated_sessions, monkeypatch
):
    from uuid import uuid4

    from app.models.curated_vocabulary import CuratedVocabulary as Word
    from app.services.policy_installation import import_policies
    from app.services.review_targets import ReviewedTargets
    from tests.test_policy_preparation import prepared_fixture

    sessions = curated_sessions
    _, _, identifier, policies = await prepared_fixture(sessions)
    async with sessions() as session, session.begin():
        await import_policies(session, policies, install=True)
    calls = []
    import app.services.policy_preparation as preparation

    original = preparation.prepare

    def tracked(entries, existing=(), **kwargs):
        calls.append(kwargs.get("only_ids"))
        return original(entries, existing, **kwargs)

    monkeypatch.setattr(preparation, "prepare", tracked)
    other = uuid4()
    async with sessions() as session:
        async with session.begin():
            word = await session.get(Word, identifier)
            session.info["review_policy_batch"] = (
                session.sync_session.get_transaction(),
                {identifier, other},
            )
            resolver = ReviewedTargets()
            assert (await resolver.resolve(session, word)).gradeable
            assert (await resolver.resolve(session, word)).gradeable
            assert calls == [{identifier, other}]
        async with session.begin():
            word = await session.get(Word, identifier)
            assert (await resolver.resolve(session, word)).gradeable
            assert calls[-1] == {identifier}
            assert len(calls) == 2
