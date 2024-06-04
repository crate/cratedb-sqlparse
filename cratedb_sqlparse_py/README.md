# CrateDB SQL Parser for Python

[![License](https://img.shields.io/github/license/crate/cratedb-sqlparse.svg)](https://github.com/crate/cratedb-sqlparse/blob/main/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/cratedb-sqlparse.svg)](https://pypi.org/project/cratedb-sqlparse/)
[![PyPI downloads](https://pepy.tech/badge/cratedb-sqlparse/month)](https://pepy.tech/project/cratedb-sqlparse/)

[![Tests](https://github.com/crate/cratedb-sqlparse/actions/workflows/python.yml/badge.svg)](https://github.com/crate/cratedb-sqlparse/actions/workflows/python.yml)
[![Test coverage](https://img.shields.io/codecov/c/gh/crate/cratedb-sqlparse.svg)](https://codecov.io/gh/crate/cratedb-sqlparse/)
[![Python versions](https://img.shields.io/pypi/pyversions/cratedb-sqlparse.svg)](https://pypi.org/project/cratedb-sqlparse/)

[![Status](https://img.shields.io/pypi/status/cratedb-sqlparse.svg)](https://pypi.org/project/cratedb-sqlparse/)

This package provides utilities to validate and split SQL statements specifically designed for CrateDB.

It is built upon CrateDB's antlr4 grammar, ensuring accurate parsing tailored to CrateDB's SQL dialect.

It draws inspiration from `sqlparse`.

## Installation.

## Usage:

```python
from cratedb_sqlparse import sqlparse

query = """
    SELECT * FROM SYS.SHARDS;
    INSERT INTO doc.tbl VALUES (1);
"""
statements = sqlparse(query, raise_exception=True)

print(len(statements))
# 2

select_query = statements[0]

print(select_query.query)
# 'SELECT * FROM SYS.SHARDS'

print(select_query.type)
# 'SELECT'

print(select_query.tree)
# (statement (query (queryNoWith (queryTerm (querySpec SELECT (selectItem *) FROM (relation (aliasedRelation (relationPrimary (table (qname (ident (unquotedIdent SYS)) . (ident (unquotedIdent (nonReserved SHARDS)))))))))))))

sqlparse('SEEELECT * FROM sys.shards')
# cratedb_sqlparse.parser.parser.ParsingException: line1:0 mismatched input 'SEEELECT' expecting {'SELECT', 'DEALLOCATE', ...}
```


## Development
```shell
git clone https://github.com/crate/cratedb-sqlparse

cd cratedb-sqlparse/cratedb_sqlparse_py
python3 -m venv .venv
source .venv/bin/activate
pip install --editable='.[develop,generate,release,test]'
poe check
```

### Run only tests
```shell
poe test
```

### Run only one test
```shell
poe test -k test_sqlparse_collects_exceptions_2
```