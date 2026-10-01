from .llm import ask
from .models import Classification
from .glossary import glossary_text

SYSTEM = """You are the routing and ambiguity-detection stage of a text-to-SQL system.
Classify the user's question:
- data_query: clear enough to write one correct SQL SELECT.
- ambiguous: could map to materially different SQL AND neither the glossary nor the defaults resolve it.
- out_of_scope: not answerable from this database.
- unsafe: asks to insert/update/delete/drop/alter or access system tables.

Rules:
- If the glossary or defaults resolve a term, it is NOT ambiguous.
- Do not flag trivial choices (column order, aliases).
- Ask at most 2 clarifying questions, short, with 2-4 concrete options when possible.
- ambiguity types: vague_term, unmapped_term, multiple_columns, missing_parameter, unresolved_reference.
- Only set ambiguities when intent is ambiguous.

Examples:
"How many customers are from India?" -> data_query
"Show recent orders" -> data_query (default 'recent' = last 30 days)
"Who are our best customers?" -> ambiguous (best by revenue or by order count?)
"Delete cancelled orders" -> unsafe
"What is the weather today?" -> out_of_scope

{glossary}

DATABASE SCHEMA:
{schema}
"""

def classify(question: str, schema: str) -> Classification:
    return ask(SYSTEM.format(glossary=glossary_text(), schema=schema), question, Classification)