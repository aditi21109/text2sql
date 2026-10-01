from .classifier import classify
from .generator import generate_sql
from .validator import validate, SQLValidationError
from .executor import run_query
from .models import PipelineResult, Intent
from .schema import load_schema
from .config import settings

_schema_text, _tables = load_schema(settings.db_url)

def answer(question: str) -> PipelineResult:
    c = classify(question, _schema_text)

    if c.intent in (Intent.UNSAFE, Intent.OUT_OF_SCOPE):
        return PipelineResult(status="refused",
                              message=f"I can't help with that ({c.intent.value}): {c.reasoning}")
    if c.intent == Intent.AMBIGUOUS and c.ambiguities:
        return PipelineResult(status="needs_clarification",
                              message="I need a bit more detail.",
                              clarifying_questions=c.ambiguities)

    err = prev_sql = None
    for _ in range(settings.max_repairs + 1):
        gen = generate_sql(question, _schema_text, err, prev_sql)
        try:
            safe_sql = validate(gen.sql, _tables)
            cols, rows = run_query(safe_sql)
            return PipelineResult(status="ok", sql=safe_sql, assumptions=gen.assumptions,
                                  columns=cols, rows=rows)
        except Exception as e:
            err, prev_sql = str(e), gen.sql
    return PipelineResult(status="error", message=f"Could not produce a valid query: {err}")