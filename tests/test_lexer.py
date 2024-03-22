import pytest

from cratedb_sqlparse import sqlparse, ParsingException


def test_sqlparser_one_statement(query=None):
    query = query or 'SELECT 1;'
    r = sqlparse(query)

    assert len(r) == 1

    stmt = r[0]

    assert stmt.query == query.replace(';', '')  # obj.query doesn't include comments or ';'
    assert stmt.original_query == query
    assert stmt.type == 'SELECT'


def test_sqlparse_several_statements():
    query = """
    SELECT 1;
    INSERT INTO doc.tbl VALUES (1,2,3,4,5,6);
    SELECT 3;
    """

    r = sqlparse(query)

    assert len(r) == 3

    test_sqlparser_one_statement(r[0].query)

    assert r[1].type == 'INSERT'
    assert r[2].type == 'SELECT'


def test_sqlparse_dollar_string():
    query = "SELECT $$crate's performance$$"
    r = sqlparse(query)

    assert r[0].query == query


def test_sqlparse_raises_exception():
    query = "SALUT MON AMIE"

    with pytest.raises(ParsingException):
        sqlparse(query)


def test_sqlparse_is_case_insensitive():
    query = "inSerT InTo doc.Tbl1 Values (1)"

    r = sqlparse(query)

    assert r[0].query == query
