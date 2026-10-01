import pytest
from app.validator import validate, SQLValidationError

TABLES = {"customers", "orders", "products", "order_items"}

def test_select_ok():
    assert "LIMIT" in validate("SELECT * FROM customers", TABLES).upper()

@pytest.mark.parametrize("sql", [
    "DROP TABLE customers",
    "SELECT 1; DELETE FROM orders",
    "SELECT * FROM pg_user",
])
def test_blocked(sql):
    with pytest.raises(SQLValidationError):
        validate(sql, TABLES)