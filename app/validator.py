import sqlglot
from sqlglot import exp
from .config import settings

FORBIDDEN = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create,
             exp.Alter, exp.Command, exp.Merge)

class SQLValidationError(Exception):
    pass

def validate(sql: str, allowed_tables: set[str]) -> str:
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except sqlglot.errors.ParseError as e:
        raise SQLValidationError(f"Syntax error: {e}")
    if len(statements) != 1 or statements[0] is None:
        raise SQLValidationError("Exactly one statement is allowed")
    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Union)):
        raise SQLValidationError("Only SELECT queries are allowed")
    if tree.find(*FORBIDDEN):
        raise SQLValidationError("Data-modifying statements are not allowed")
    cte_names = {c.alias for c in tree.find_all(exp.CTE)}
    used = {t.name for t in tree.find_all(exp.Table)} - cte_names
    unknown = used - allowed_tables
    if unknown:
        raise SQLValidationError(f"Unknown or disallowed tables: {sorted(unknown)}")
    if not tree.args.get("limit"):
        tree = tree.limit(settings.max_rows)
    return tree.sql(dialect="postgres")