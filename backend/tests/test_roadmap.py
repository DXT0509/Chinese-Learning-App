from uuid import uuid4

import httpx
import pytest
from pydantic import ValidationError

from app.main import create_app
from app.schemas.roadmap import Activity, ActivitySubmission, RoadmapDefinition
from app.services.roadmap import evaluate


def draft(words=None, interval=3, **changes):
    words = words or [(uuid4(), 1) for _ in range(3)]
    nodes, group = [], []
    for index, (identifier, version) in enumerate(words):
        ref = {"vocabulary_id": str(identifier), "content_version": version}
        group.append(ref)
        nodes.append(
            {
                "id": str(uuid4()),
                "position": len(nodes),
                "node_type": "NEW_WORD",
                "title": f"Từ {index + 1}",
                "lesson": {
                    "vocabulary": [ref],
                    "activities": [
                        {"id": str(uuid4()), "kind": "INTRODUCTION", "prompt": "Đọc từ"}
                    ],
                },
            }
        )
        if len(group) == interval or index == len(words) - 1:
            nodes.append(
                {
                    "id": str(uuid4()),
                    "position": len(nodes),
                    "node_type": "REVIEW",
                    "title": "Ôn tập",
                    "lesson": {
                        "vocabulary": group,
                        "activities": [
                            {
                                "id": str(uuid4()),
                                "kind": "QUIZ",
                                "prompt": "Chọn đáp án",
                                "options": ["đúng", "sai"],
                                "correct_option": 0,
                                "evaluation": "EXACT_CHOICE",
                            }
                        ],
                    },
                }
            )
            group = []
    return RoadmapDefinition.model_validate(
        {
            "id": str(uuid4()),
            "code": f"test-{uuid4()}",
            "version": 1,
            "title": "HSK 0",
            "review_interval": interval,
            "nodes": nodes,
            **changes,
        }
    )


def test_one_word_grouping_and_configurable_interval():
    assert [n.node_type for n in draft().nodes] == ["NEW_WORD"] * 3 + ["REVIEW"]
    assert [n.node_type for n in draft(interval=1).nodes] == ["NEW_WORD", "REVIEW"] * 3
    assert draft(interval=10).nodes[-1].node_type == "REVIEW"


@pytest.mark.parametrize(
    "case",
    [
        "two_words",
        "duplicate",
        "future",
        "order",
        "missing_review",
        "scope_version",
        "unreviewed_required",
        "empty_activities",
    ],
)
def test_invalid_drafts(case):
    data = draft().model_dump(mode="json")
    if case == "two_words":
        data["nodes"][0]["lesson"]["vocabulary"] += data["nodes"][1]["lesson"]["vocabulary"]
    elif case == "duplicate":
        data["nodes"][1]["id"] = data["nodes"][0]["id"]
    elif case == "future":
        data["nodes"][-1]["lesson"]["vocabulary"][0]["vocabulary_id"] = str(uuid4())
    elif case == "order":
        data["nodes"][0]["position"] = 4
    elif case == "missing_review":
        data["nodes"].pop()
    elif case == "scope_version":
        data["nodes"][-1]["lesson"]["vocabulary"][0]["content_version"] = 2
    elif case == "unreviewed_required":
        data["nodes"][0]["lesson"]["audio"] = {"required": True, "status": "UNREVIEWED"}
    else:
        data["nodes"][0]["lesson"]["activities"] = []
    with pytest.raises(ValidationError):
        RoadmapDefinition.model_validate(data)


def test_evidence_is_not_a_completion_flag():
    with pytest.raises(ValidationError):
        ActivitySubmission.model_validate({"completed": True})
    activity = Activity(
        id=uuid4(),
        kind="QUIZ",
        prompt="Pick",
        options=["a", "b"],
        correct_option=1,
        evaluation="EXACT_CHOICE",
    )
    evidence = ActivitySubmission(
        request_id=uuid4(), activity_id=activity.id, kind="CHOICE", choice=0
    )
    assert not evaluate(activity, evidence)
    assert evaluate(activity, evidence.model_copy(update={"choice": 1}))
    writing = Activity(id=uuid4(), kind="HANDWRITING", prompt="Write")
    assert not evaluate(writing, evidence.model_copy(update={"kind": "FREEHAND", "choice": None}))


async def test_all_roadmap_routes_require_authentication():
    identifier = uuid4()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        for method, path, body in [
            ("GET", "/roadmaps", None),
            ("GET", f"/roadmaps/{identifier}/nodes", None),
            ("GET", f"/roadmap-nodes/{identifier}", None),
            ("POST", f"/roadmap-nodes/{identifier}/start", {}),
            ("POST", f"/roadmap-nodes/{identifier}/skip", None),
            ("POST", f"/roadmap-runs/{identifier}/complete", None),
            ("POST", f"/roadmap-runs/{identifier}/activities", {}),
            ("GET", "/me/roadmap-progress", None),
        ]:
            assert (await client.request(method, "/api/v1" + path, json=body)).status_code == 401
