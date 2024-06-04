def test_sqlparser_one_statement(query=None):
    from cratedb_sqlparse import sqlparse

    query = query or "SELECT 1;"
    r = sqlparse(query)

    assert len(r) == 1

    stmt = r[0]

    assert stmt.query == query.replace(";", "")  # obj.query doesn't include comments or ';'
    assert stmt.original_query == query
    assert stmt.type == "SELECT"


def test_sqlparse_several_statements():
    from cratedb_sqlparse import sqlparse

    query = """
    SELECT 1;
    INSERT INTO doc.tbl VALUES (1,2,3,4,5,6);
    SELECT 3;
    """

    r = sqlparse(query)

    assert len(r) == 3

    test_sqlparser_one_statement(r[0].query)

    assert r[1].type == "INSERT"
    assert r[2].type == "SELECT"


def test_sqlparse_dollar_string():
    from cratedb_sqlparse import sqlparse

    query = "update test set a=$$test;test$$"
    r = sqlparse(query)

    assert r[0].query == query


def test_sqlparse_multiquery_edge_case():
    # Test for https://github.com/crate/cratedb-sqlparse/issues/28,
    # if this ends up parsing 3 statements, we can change this test,
    # it's here so we can programmatically track if the behavior changes.
    from cratedb_sqlparse import sqlparse

    query = """
    SELECT A FROM tbl1 where ;
    SELEC 1;
    SELECT D, A FROM tbl1 WHERE;
"""

    statements = sqlparse(query)
    assert len(statements) == 1


def test_sqlparse_is_case_insensitive():
    from cratedb_sqlparse import sqlparse

    query = "inSerT InTo doc.Tbl1 Values (1)"

    r = sqlparse(query)

    assert r[0].query == query
