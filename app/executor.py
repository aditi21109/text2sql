import psycopg
from .config import settings

def run_query(sql: str) -> tuple[list[str], list[list]]:
    with psycopg.connect(settings.db_url) as conn:
        conn.read_only = True
        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = 5000")
            cur.execute(sql)
            cols = [d.name for d in cur.description]
            rows = [list(r) for r in cur.fetchmany(settings.max_rows)]
    return cols, rows