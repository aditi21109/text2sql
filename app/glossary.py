GLOSSARY = {
    "revenue / sales": "SUM(orders.total_amount) over orders WHERE status = 'completed'",
    "active customer": "customer with at least 1 completed order in the last 90 days",
    "AOV": "average of orders.total_amount for completed orders",
}

DEFAULTS = {
    "recent / lately": "last 30 days",
    "top / best (no number given)": "top 10",
    "month (no year given)": "current year",
}

def glossary_text() -> str:
    g = "\n".join(f"- {k}: {v}" for k, v in GLOSSARY.items())
    d = "\n".join(f"- {k}: {v}" for k, v in DEFAULTS.items())
    return f"BUSINESS GLOSSARY:\n{g}\n\nDEFAULTS (apply and state as assumption, don't ask):\n{d}"