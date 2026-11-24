"""Strict authoring and learner contracts. No catalog prose is copied into lessons."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class VocabularyReference(Contract):
    vocabulary_id: UUID
    content_version: Annotated[int, Field(strict=True, ge=1)]


class Enrichment(Contract):
    status: Literal["AVAILABLE", "UNAVAILABLE", "UNREVIEWED"] = "UNAVAILABLE"
    required: bool = False
    asset_id: UUID | None = None
    text: Annotated[str, Field(min_length=1, max_length=4000)] | None = None

    @model_validator(mode="after")
    def availability(self):
        if self.status == "AVAILABLE" and not (self.text or self.asset_id):
            raise ValueError("available enrichment requires content")
        if self.status != "AVAILABLE" and (self.text or self.asset_id):
            raise ValueError("unavailable/unreviewed content cannot be rendered")
        if self.required and self.status != "AVAILABLE":
            raise ValueError("required enrichment must be reviewed and available")
        return self


class Component(Contract):
    character_position: Annotated[int, Field(ge=0)]
    component: Annotated[str, Field(min_length=1, max_length=20)]
    role: Literal["SEMANTIC_RADICAL", "PHONETIC", "STRUCTURAL"]
    explanation: Enrichment


class Activity(Contract):
    id: UUID
    kind: Literal[
        "INTRODUCTION", "COMPONENTS", "STROKE_ORDER", "HANDWRITING", "QUIZ", "PRONUNCIATION"
    ]
    required: bool = True
    prompt: Annotated[str, Field(min_length=1, max_length=2000)]
    repetitions: Annotated[int, Field(strict=True, ge=1, le=20)] = 1
    options: Annotated[list[str], Field(max_length=10)] = []
    correct_option: Annotated[int, Field(strict=True, ge=0)] | None = None
    # Server checks participation only for writing/speaking; never quality scores.
    evaluation: Literal["PARTICIPATION", "EXACT_CHOICE"] = "PARTICIPATION"
    preserve_freehand: Literal[True] = True
    automatic_snapping: Literal[False] = False

    @model_validator(mode="after")
    def evaluator(self):
        if self.kind == "QUIZ":
            if (
                self.evaluation != "EXACT_CHOICE"
                or self.correct_option is None
                or not 2 <= len(self.options)
                or self.correct_option >= len(self.options)
            ):
                raise ValueError("quiz requires server-owned answer")
            if len(set(self.options)) != len(self.options):
                raise ValueError("duplicate quiz choices")
        elif self.correct_option is not None or self.options or self.evaluation != "PARTICIPATION":
            raise ValueError("unsupported evaluator")
        return self


class LessonDefinition(Contract):
    schema_version: Literal[1] = 1
    vocabulary: Annotated[list[VocabularyReference], Field(min_length=1, max_length=100)]
    audio: Enrichment = Enrichment()
    examples: Enrichment = Enrichment()
    notes: Enrichment = Enrichment()
    stroke_order: Enrichment = Enrichment()
    components: Annotated[list[Component], Field(max_length=100)] = []
    activities: Annotated[list[Activity], Field(min_length=1, max_length=100)]

    @model_validator(mode="after")
    def unique(self):
        if len({v.vocabulary_id for v in self.vocabulary}) != len(self.vocabulary):
            raise ValueError("duplicate vocabulary")
        if len({a.id for a in self.activities}) != len(self.activities):
            raise ValueError("duplicate activity")
        if not any(a.required for a in self.activities):
            raise ValueError("explicit completion requirements are mandatory")
        return self


class NodeDefinition(Contract):
    id: UUID
    position: Annotated[int, Field(strict=True, ge=0)]
    node_type: Literal["NEW_WORD", "REVIEW"]
    title: Annotated[str, Field(min_length=1, max_length=255)]
    section: Annotated[str, Field(min_length=1, max_length=100)] = "hsk-0"
    visual: Annotated[
        dict[
            Annotated[str, Field(min_length=1, max_length=40)],
            Annotated[str, Field(max_length=200)],
        ],
        Field(max_length=8),
    ] = {}
    lesson: LessonDefinition

    @model_validator(mode="after")
    def one_word(self):
        if self.node_type == "NEW_WORD" and len(self.lesson.vocabulary) != 1:
            raise ValueError("NEW_WORD requires exactly one vocabulary identity")
        return self


class Rewards(Contract):
    new_word: Annotated[int, Field(strict=True, ge=0, le=10000)] = 10
    review: Annotated[int, Field(strict=True, ge=0, le=10000)] = 15


class RoadmapDefinition(Contract):
    schema_version: Literal[1] = 1
    id: UUID
    code: Annotated[str, Field(pattern=r"^[a-z0-9-]{1,100}$")]
    version: Annotated[int, Field(strict=True, ge=1)]
    title: Annotated[str, Field(min_length=1, max_length=255)]
    review_interval: Annotated[int, Field(strict=True, ge=1, le=100)] = 3
    allow_review_skip: bool = False
    rewards: Rewards = Rewards()
    nodes: Annotated[list[NodeDefinition], Field(min_length=1, max_length=10000)]

    @model_validator(mode="after")
    def ordering(self):
        if [n.position for n in self.nodes] != list(range(len(self.nodes))):
            raise ValueError("positions must be contiguous, ordered and start at zero")
        if len({n.id for n in self.nodes}) != len(self.nodes):
            raise ValueError("duplicate stable nodes")
        introduced, group = set(), []
        for node in self.nodes:
            scope = [(v.vocabulary_id, v.content_version) for v in node.lesson.vocabulary]
            if node.node_type == "NEW_WORD":
                if len(group) >= self.review_interval or scope[0][0] in introduced:
                    raise ValueError("missing review or duplicate introduction")
                introduced.add(scope[0][0])
                group.extend(scope)
            else:
                if not group or scope != group:
                    raise ValueError("review must cover the exact preceding group in order")
                group = []
        if group:
            raise ValueError("final group requires an explicit review (may be shorter)")
        return self


class StartRequest(Contract):
    replay: bool = False
    request_id: UUID | None = None

    @model_validator(mode="after")
    def replay_identity(self):
        if self.replay and self.request_id is None:
            raise ValueError("replay requires a client-generated request_id")
        return self


class Point(Contract):
    x: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
    y: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class ActivitySubmission(Contract):
    request_id: UUID
    activity_id: UUID
    kind: Literal["ACKNOWLEDGE", "CHOICE", "FREEHAND", "SPEAKING"]
    choice: Annotated[int, Field(strict=True, ge=0, le=9)] | None = None
    strokes: Annotated[
        list[Annotated[list[Point], Field(min_length=2, max_length=1000)]], Field(max_length=100)
    ] = []
    repetition: Annotated[int, Field(strict=True, ge=0, le=19)] = 0
    duration_ms: Annotated[int, Field(strict=True, ge=0, le=300000)] = 0


class NodeSummary(Contract):
    id: UUID
    node_version_id: UUID
    position: int
    node_type: Literal["NEW_WORD", "REVIEW"]
    title: str
    section: str
    visual: dict[str, str]
    status: Literal["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "SKIPPED"]
    available: bool


class NodePage(Contract):
    roadmap_version_id: UUID
    items: list[NodeSummary]
    next_position: int | None
    current_position: int | None = None
    section_positions: dict[str, int] = {}


class RoadmapSummary(Contract):
    id: UUID
    version_id: UUID
    code: str
    version: int
    title: str


class RoadmapPage(Contract):
    items: list[RoadmapSummary]
    next_offset: int | None


class RunView(Contract):
    id: UUID
    node_version_id: UUID
    replay: bool
    completed_at: datetime | None
    accepted_activity_ids: list[UUID]
    accepted_repetitions: dict[str, list[int]] = {}


class CompletionResult(Contract):
    status: Literal["COMPLETED", "SKIPPED"]
    exp_awarded: int


class ReceiptResult(Contract):
    accepted: bool
    evaluator: str


class ProgressSummary(Contract):
    total_exp: int
    completed_nodes: int
    skipped_nodes: int


class NodeDetail(Contract):
    node_version_id: UUID
    lesson_version_id: UUID
    definition: dict
    vocabulary: list[dict]
