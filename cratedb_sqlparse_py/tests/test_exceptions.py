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

    # Different combination of the queries to validate
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

    # Different combination of the queries to validate
    r = sqlparse("""
        SELECT 1;
        SELECT A, B, C, D FROM tbl1;
        INSERT INTO doc.tbl VALUES (1,2, 'three', ['four']);
    """)

    assert r[0].exception is None
    assert r[1].exception is None
    assert r[2].exception is None


def test_sqlparse_catches_exception():
    """
    Special characters should not stop sqlparse from creating and matching the exception.

    See https://github.com/crate/cratedb-sqlparse/issues/67
    """
    from cratedb_sqlparse import sqlparse

    stmts = """
        SELECT 1\n limit,
        SELECT 1\r limit,
        SELECT 1\t limit,
        SELECT 1 limit
    """
    for stmt in stmts:
        assert sqlparse(stmt)[0].exception


def test_sqlparse_should_not_panic():
    """
    Missing token ')' in this case, should not throw a Runtime Exception.

    See https://github.com/crate/cratedb-sqlparse/issues/66
    """
    from cratedb_sqlparse import sqlparse

    sqlparse("""
        CREATE TABLE t01 (
           "x" OBJECT (DYNAMIC),
           "y" OBJECT (DYNAMIC) AS ("z" ARRAY(OBJECT (DYNAMIC))
           );
    """)[0]


def test_sqlparse_match_exceptions_spaces():
    """
    Regardless of spaces, errors should be correctly matched to their original statement.

    See https://github.com/crate/cratedb-sqlparse/issues/107
    """
    from cratedb_sqlparse import sqlparse

    stmts = [
        """
        SELECT A FROM tbl1 where ;
        SELECT 1;
        SELECT D, A FROM tbl1 WHERE;
        """,
        """
        SELECT
          A
        FROM
          tbl1
        WHERE;

        SELECT
          1;

        SELECT
          B
        FROM
          tbl1
        WHERE;
        """,
    ]

    for stmt in stmts:
        r = sqlparse(stmt)
        assert r[0]
        assert r[1]
        assert r[2]


def test_sqlparse_match_exception_missing_eof():
    """
    Statements that miss an eof should be detected as one, and catch the appropriate exception

    See https://github.com/crate/cratedb-sqlparse/issues/113
    """
    from cratedb_sqlparse import sqlparse

    stmts = [
        """
        select 1;
        select 2
        select 3;
        """,
        """
        select 1;
        select 1 I can put anything here
        select 3
        """,
    ]
    for stmt in stmts:
        r = sqlparse(stmt)
        assert len(r) == 2
        assert not r[0].exception
        assert r[1].exception
