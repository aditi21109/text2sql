from .llm import ask
from .models import SQLResult
from .glossary import glossary_text

SYSTEM = """You write PostgreSQL SELECT queries.
Rules:
- Output a single read-only SELECT (CTEs allowed). Never modify data.
- Use only tables/columns in the schema. Never invent columns.
- Apply glossary definitions and defaults exactly; list each one used in `assumptions`.
- Qualify columns with table aliases in joins.
- confidence: 0-1, lower it if you guessed anything.

{glossary}

DATABASE SCHEMA:
{schema}
"""

def generate_sql(question: str, schema: str, previous_error: str | None = None,
                 previous_sql: str | None = None) -> SQLResult:
    user = question
    if previous_error:
        user += f"\n\nYour previous SQL failed.\nSQL: {previous_sql}\nError: {previous_error}\nFix it."
    return ask(SYSTEM.format(glossary=glossary_text(), schema=schema), user, SQLResult)