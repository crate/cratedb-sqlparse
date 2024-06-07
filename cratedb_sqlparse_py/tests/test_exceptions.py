import pytest


def test_exception_message():
    from cratedb_sqlparse import sqlparse

    r = sqlparse("""
         SELEC 1;
        SELECT A, B, C, D FROM tbl1;
        SELECT D, A FROM tbl1 WHERE;
    """)
    expected_message = "InputMismatchException[line 2:9 mismatched input 'SELEC' expecting {'SELECT', 'DEALLOCATE', 'FETCH', 'END', 'WITH', 'CREATE', 'ALTER', 'KILL', 'CLOSE', 'BEGIN', 'START', 'COMMIT', 'ANALYZE', 'DISCARD', 'EXPLAIN', 'SHOW', 'OPTIMIZE', 'REFRESH', 'RESTORE', 'DROP', 'INSERT', 'VALUES', 'DELETE', 'UPDATE', 'SET', 'RESET', 'COPY', 'GRANT', 'DENY', 'REVOKE', 'DECLARE'}]"  # noqa
    expected_message_2 = "\n         SELEC 1;\n         ^^^^^\n        SELECT A, B, C, D FROM tbl1;\n        SELECT D, A FROM tbl1 WHERE;\n    "  # noqa
    assert r[0].exception.error_message == expected_message
    assert r[0].exception.original_query_with_error_marked == expected_message_2


def test_sqlparse_raises_exception():
    from cratedb_sqlparse import ParsingException, sqlparse

    query = "SELCT 2"

    with pytest.raises(ParsingException):
        sqlparse(query, raise_exception=True)


def test_sqlparse_not_raise_exception():
    from cratedb_sqlparse import sqlparse

    sqlparse("SELECT COUNT(*) FROM doc.tbl f WHERE f.id = 1;", raise_exception=True)


def test_sqlparse_collects_exception():
    from cratedb_sqlparse import sqlparse

    query = "SELCT 2"

    statements = sqlparse(query)
    assert statements[0]


def test_sqlparse_collects_exceptions():
    from cratedb_sqlparse import sqlparse

    r = sqlparse("""
        SELECT A FROM tbl1 where ;
        SELECT 1;
        SELECT D, A FROM tbl1 WHERE;
    """)

    assert len(r) == 3

    assert r[0].exception is not None
    assert r[1].exception is None
    assert r[2].exception is not None


def test_sqlparse_collects_exceptions_2():
    from cratedb_sqlparse import sqlparse

    # Different combination of the query to validate
    r = sqlparse("""
         SELEC 1;
        SELECT A, B, C, D FROM tbl1;
        SELECT D, A FROM tbl1 WHERE;
    """)

    assert r[0].exception is not None
    assert r[1].exception is None
    assert r[2].exception is not None


def test_sqlparse_collects_exceptions_3():
    from cratedb_sqlparse import sqlparse

    # Different combination of the query to validate
    r = sqlparse("""
        SELECT 1;
        SELECT A, B, C, D FROM tbl1;
        INSERT INTO doc.tbl VALUES (1,2, 'three', ['four']);
    """)

    assert r[0].exception is None
    assert r[1].exception is None
    assert r[2].exception is None
