from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field

class Intent(str, Enum):
    DATA_QUERY = "data_query"
    AMBIGUOUS = "ambiguous"
    OUT_OF_SCOPE = "out_of_scope"
    UNSAFE = "unsafe"

class Ambiguity(BaseModel):
    type: Literal["vague_term", "unmapped_term", "multiple_columns",
                  "missing_parameter", "unresolved_reference"]
    phrase: str = Field(description="The words in the question that are ambiguous")
    question: str = Field(description="One short clarifying question for the user")
    options: list[str] = Field(default_factory=list)

class Classification(BaseModel):
    intent: Intent
    reasoning: str
    ambiguities: list[Ambiguity] = Field(default_factory=list)

class SQLResult(BaseModel):
    sql: str
    assumptions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)

class PipelineResult(BaseModel):
    status: Literal["ok", "needs_clarification", "refused", "error"]
    message: str = ""
    clarifying_questions: list[Ambiguity] = Field(default_factory=list)
    sql: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)