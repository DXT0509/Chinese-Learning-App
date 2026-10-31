"""Reviewed lexical classification is distinct from a contextual grammatical role."""

from typing import Literal

from pydantic import Field, model_validator

from app.schemas.curated_vocabulary import StrictRecord, Text, is_hanzi

POLICY_VERSION = "contextual-grammar-v1"
ROLE_OPTIONS = (
    "subject",
    "predicate",
    "object",
    "attribute",
    "adverbial",
    "complement",
    "modal_modifier",
    "independent_clause",
)
EXPRESSION_OPTIONS = ("greeting", "farewell", "gratitude", "apology", "wish")
MORPHEME_OPTIONS = ("independent_word", "bound_morpheme", "independent_clause", "greeting")
FUNCTION_OPTIONS = ("noun", "verb", "adjective", "adverb", "quantity_phrase")


class ContextualGrammar(StrictRecord):
    lexical_category: Literal["idiom", "expression", "bound_morpheme", "quantity_expression"]
    assessment: Literal[
        "SYNTACTIC_ROLE", "GRAMMATICAL_FUNCTION", "EXPRESSION_KIND", "MORPHEME_KIND"
    ]
    source_part_of_speech: Text
    source_example: Text
    context_simplified: Text
    rationale: Text
    question_vi: Text
    occurrence: int = Field(default=0, ge=0, strict=True)

    @model_validator(mode="after")
    def reviewed_context(self):
        if not any(is_hanzi(c) for c in self.source_example + self.context_simplified):
            raise ValueError("Actual Chinese source and assessment context required")
        if any(is_hanzi(c) for c in self.question_vi):
            raise ValueError("Question instructions must be Vietnamese")
        if self.assessment == "MORPHEME_KIND" and self.lexical_category != "bound_morpheme":
            raise ValueError("Morpheme assessment requires a bound-morpheme review")
        if self.assessment == "EXPRESSION_KIND" and self.lexical_category != "expression":
            raise ValueError("Expression assessment requires an expression review")
        return self

    @property
    def options(self):
        return {
            "SYNTACTIC_ROLE": ROLE_OPTIONS,
            "EXPRESSION_KIND": EXPRESSION_OPTIONS,
            "MORPHEME_KIND": MORPHEME_OPTIONS,
            "GRAMMATICAL_FUNCTION": FUNCTION_OPTIONS,
        }[self.assessment]

    def validate_word(self, word):
        if self.source_part_of_speech != word.part_of_speech:
            raise ValueError("Contextual grammar source POS changed")
        # This is a refinement of a broad structural label, never an override of
        # an explicitly conflicting dictionary POS or a blanket missing-POS pass.
        source = self.source_part_of_speech
        if source not in {
            "idiom",
            "phrase",
            "phrase; modal",
            "phrase; time",
            "phrase; locality",
            "phrase; adverb",
            "verb phrase",
            "word element",
            "quantifier",
        }:
            raise ValueError("Contextual refinement requires a reviewed structural source label")
        if self.lexical_category == "idiom" and source != "idiom":
            raise ValueError("Idiom classification lacks source support")
        if self.lexical_category == "bound_morpheme" and source != "word element":
            raise ValueError("Bound-morpheme classification lacks source support")
        if self.lexical_category == "quantity_expression" and source != "quantifier":
            raise ValueError("Quantity classification lacks source support")
        count = self.context_simplified.count(word.simplified)
        if count <= self.occurrence or word.simplified not in self.source_example:
            raise ValueError("Reviewed context must contain the exact lexical form")

    def prompt(self, word):
        self.validate_word(word)
        # Chinese appears only at POS, after Hanzi and Pinyin have been answered.
        chunks = self.context_simplified.split(word.simplified)
        marked = chunks[0]
        for index, chunk in enumerate(chunks[1:]):
            marked += (
                f"【{word.simplified}】" if index == self.occurrence else word.simplified
            ) + chunk
        return self.question_vi + "\n" + marked
