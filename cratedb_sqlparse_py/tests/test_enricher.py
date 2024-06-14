def test_table_metadata():
    from cratedb_sqlparse import sqlparse
    from cratedb_sqlparse.parser import Metadata

    query = "SELECT 1; SELECT 2;"
    stmts = sqlparse(query)
    for stmt in stmts:
        assert hasattr(stmt, "metadata")
        assert isinstance(stmt.metadata, Metadata)


def test_table_name_statement():
    from cratedb_sqlparse import sqlparse

    query = "CREATE TABLE doc.tbl2 (a TEXT)"

    stmts = sqlparse(query)
    stmt = stmts[0]

    assert stmt.metadata.schema == "doc"
    assert stmt.metadata.table_name == "tbl2"


def test_table_name_statements():
    from cratedb_sqlparse import sqlparse

    query = """
    SELECT A,B,C,D,E FROM doc.tbl1;
    SELECT A,B FROM "doc"."tbl1";
    SELECT A,B FROM "tbl1";
    SELECT A,B FROM tbl1;
    """

    stmts = sqlparse(query=query)

    assert stmts[0].metadata.schema == "doc"
    assert stmts[0].metadata.table_name == "tbl1"

    assert stmts[1].metadata.schema == "doc"
    assert stmts[1].metadata.table_name == "tbl1"

    assert stmts[2].metadata.schema is None
    assert stmts[2].metadata.table_name == "tbl1"

    assert stmts[3].metadata.schema is None
    assert stmts[3].metadata.table_name == "tbl1"


def test_table_with_properties():
    from cratedb_sqlparse import sqlparse

    query = "CREATE TABLE tbl (A TEXT) WITH ('key' = 'val', 'key2' = 2, 'key3' = true)"

    stmt = sqlparse(query)[0]
    keys = ["key", "key2"]

    assert all(x in stmt.metadata.with_properties for x in keys)
    assert stmt.metadata.with_properties["key"] == "val"
    assert stmt.metadata.with_properties["key2"] == "2"
    assert stmt.metadata.with_properties["key3"] == "true"


def test_with_with_parameterized_properties():
    from cratedb_sqlparse import sqlparse

    query = "CREATE TABLE tbl (A TEXT) WITH ('key' = $1, 'key2' = '$2')"

    stmt = sqlparse(query)[0]
    keys = ["key", "key2"]

    # Has all the keys.
    assert all(x in stmt.metadata.parameterized_properties for x in keys)
    assert all(x in stmt.metadata.with_properties for x in keys)
    assert stmt.metadata.with_properties["key"] == "$1"
    assert stmt.metadata.with_properties["key2"] == "$2"
