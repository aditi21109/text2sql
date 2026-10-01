import psycopg

COLS = """select table_name, column_name, data_type from information_schema.columns
          where table_schema='public' order by table_name, ordinal_position"""
FKS = """select tc.table_name, kcu.column_name, ccu.table_name, ccu.column_name
         from information_schema.table_constraints tc
         join information_schema.key_column_usage kcu
           on tc.constraint_name=kcu.constraint_name and tc.table_schema=kcu.table_schema
         join information_schema.constraint_column_usage ccu
           on ccu.constraint_name=tc.constraint_name and ccu.table_schema=tc.table_schema
         where tc.constraint_type='FOREIGN KEY' and tc.table_schema='public'"""

def load_schema(db_url: str) -> tuple[str, set[str]]:
    tables: dict[str, list[str]] = {}
    with psycopg.connect(db_url) as conn, conn.cursor() as cur:
        cur.execute(COLS)
        for t, c, d in cur.fetchall():
            tables.setdefault(t, []).append(f"{c} {d}")
        cur.execute(FKS)
        fks = [f"{a}.{b} -> {c}.{d}" for a, b, c, d in cur.fetchall()]
    text = "\n".join(f"TABLE {t}({', '.join(cols)})" for t, cols in tables.items())
    text += "\nFOREIGN KEYS:\n" + "\n".join(fks)
    return text, set(tables)