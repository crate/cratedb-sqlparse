def test_table_metadata():
    from cratedb_sqlparse import sqlparse
    from cratedb_sqlparse.models import Metadata

    query = "SELECT 1; SELECT 2;"
    stmts = sqlparse(query)
    for stmt in stmts:
        assert hasattr(stmt, "metadata")
        assert isinstance(stmt.metadata, Metadata)


def test_table_with_properties():
    from cratedb_sqlparse import sqlparse

    query = "CREATE TABLE tbl (A TEXT) WITH ('key' = 'val', 'key2' = 2, 'key3' = true)"

    stmt = sqlparse(query)[0]
    expected = {"key": "val", "key2": "2", "key3": "true"}

    assert stmt.metadata.with_properties == expected


def test_with_with_parameterized_properties():
    from cratedb_sqlparse import sqlparse

    query = "CREATE TABLE tbl (A TEXT) WITH ('key' = $1, 'key2' = '$2')"

    stmt = sqlparse(query)[0]
    expected = {"key": "$1", "key2": "$2"}

    # Has all the keys.
    assert stmt.metadata.with_properties == expected
    assert stmt.metadata.parameterized_properties == expected


def test_table_names():
    from cratedb_sqlparse import sqlparse

    query = "SELECT _ FROM a.b, d"

    stmt = sqlparse(query)[0]

    assert len(stmt.metadata.tables) == 2
    assert stmt.metadata.tables[0].schema == "a"
    assert stmt.metadata.tables[0].name == "b"
    assert stmt.metadata.tables[0].fqn == '"a"."b"'

    assert stmt.metadata.tables[1].schema is None
    assert stmt.metadata.tables[1].name == "d"
    assert stmt.metadata.tables[1].fqn == '"d"'
