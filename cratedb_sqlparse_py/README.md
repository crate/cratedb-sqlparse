# CrateDB SQL Parser for Python

[![License](https://img.shields.io/github/license/crate/cratedb-sqlparse.svg)](https://github.com/crate/cratedb-sqlparse/blob/main/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/cratedb-sqlparse.svg)](https://pypi.org/project/cratedb-sqlparse/)
[![PyPI downloads](https://pepy.tech/badge/cratedb-sqlparse/month)](https://pepy.tech/project/cratedb-sqlparse/)

[![Tests](https://github.com/crate/cratedb-sqlparse/actions/workflows/python.yml/badge.svg)](https://github.com/crate/cratedb-sqlparse/actions/workflows/python.yml)
[![Test coverage](https://img.shields.io/codecov/c/gh/crate/cratedb-sqlparse.svg)](https://codecov.io/gh/crate/cratedb-sqlparse/)
[![Python versions](https://img.shields.io/pypi/pyversions/cratedb-sqlparse.svg)](https://pypi.org/project/cratedb-sqlparse/)

[![Status](https://img.shields.io/pypi/status/cratedb-sqlparse.svg)](https://pypi.org/project/cratedb-sqlparse/)

This package provides utilities to validate and split SQL statements specifically designed for
CrateDB.

It is built upon CrateDB's antlr4 grammar, ensuring accurate parsing tailored to CrateDB's SQL
dialect.

It draws inspiration from `sqlparse`.

## Installation.

```shell
pip install cratedb-sqlparse
```

## Usage.

### Simple example

```python
from cratedb_sqlparse import sqlparse

query = """
    SELECT * FROM SYS.SHARDS;
    INSERT INTO doc.tbl VALUES (1);
"""
statements = sqlparse(query)

print(len(statements))
# 2

select_query = statements[0]

print(select_query.query)
# 'SELECT * FROM SYS.SHARDS'

print(select_query.type)
# 'SELECT'

print(select_query.tree)
# (statement (query (queryNoWith (queryTerm (querySpec SELECT (selectItem *) FROM (relation (aliasedRelation (relationPrimary (table (qname (ident (unquotedIdent SYS)) . (ident (unquotedIdent (nonReserved SHARDS)))))))))))))
```

### Exceptions and errors.

By default exceptions are stored in `statement.exception`

```python
from cratedb_sqlparse import sqlparse

query = """
SELECT COUNT(*) FROM doc.tbl f HERE f.id = 1;

INSERT INTO doc.tbl VALUES (1, 23, 4);
"""
statements = sqlparse(query)
stmt = statements[0]

if stmt.exception:
    print(stmt.exception.error_message)
    # InputMismatchException[line 2:31 mismatched input 'HERE' expecting {<EOF>, ';'}]

    print(stmt.exception.original_query_with_error_marked)
    # SELECT COUNT(*) FROM doc.tbl f HERE f.id = 1;
    #                                ^^^^
    # 
    # INSERT INTO doc.tbl VALUES (1, 23, 4);

    print(stmt.exception.offending_token.text)
    # HERE
```

In some situations, you might want sqlparse to raise an exception.

You can set `raise_exception` to `True`

```python
from cratedb_sqlparse import sqlparse

sqlparse('SELECT COUNT(*) FROM doc.tbl f WHERE .id = 1;', raise_exception=True)

# cratedb_sqlparse.parser.ParsingException: NoViableAltException[line 1:37 no viable alternative at input 'SELECT COUNT(*) FROM doc.tbl f WHERE .']
```

Catch the exception:

```python
from cratedb_sqlparse import sqlparse, ParsingException

try:
    t = sqlparse('SELECT COUNT(*) FROM doc.tbl f WHERE .id = 1;', raise_exception=True)[0]
except ParsingException:
    print('Catched!')
```

Note:

It will only raise the first exception it finds, even if you pass in several statements.

### Query metadata.

Query metadata can be read with `statement.metadata`

```python
from cratedb_sqlparse import sqlparse

stmt = sqlparse("SELECT A, B FROM doc.tbl12")

print(stmt.metadata)
# Metadata(tables=[Table(schema='doc', name='tbl12')], parameterized_properties={}, with_properties={})
```

#### Query properties.

Properties defined within a `WITH` statement, `statement.metadata.with_properties`.


```python
from cratedb_sqlparse import sqlparse

stmt = sqlparse("""
    CREATE TABLE doc.tbl12 (A TEXT) WITH (
      "allocation.max_retries" = 5,
      "blocks.metadata" = false
    );
""")[0]

print(stmt.metadata)
# Metadata(tables=[Table(schema='doc', name='tbl12')], with_properties={'allocation.max_retries': '5', 'blocks.metadata': 'false'})
```

#### Table name
```python
print(stmt.metadata.tables)
# [Table(schema='doc', name='tbl12')]

table = stmt.metadata.tables[0]
print(table.schema, table.name, table.fqn, sep='\n')
# doc
# tbl12
# '"doc"."tbl12"'
```



#### Parameterized properties.

Parameterized properties are properties without a real defined value, marked with a dollar string,  `metadata.parameterized_properties`

```python
from cratedb_sqlparse import sqlparse

stmt = sqlparse("""
    CREATE TABLE doc.tbl12 (A TEXT) WITH (
    "allocation.max_retries" = 5,
    "blocks.metadata" = $1
);
""")[0]

print(stmt.metadata)
# Metadata(tables=[Table(schema='doc', name='tbl12')], parameterized_properties={'blocks.metadata': '$1'}, with_properties={'allocation.max_retries': '5', 'blocks.metadata': '$1'})
```

In this case, `blocks.metadata` will be in `with_properties` and `parameterized_properties` as well.

For values to be picked up they need to start with a dollar `'$'` and be preceded by integers, e.g. `'$1'`, `'$123'` -
`'$123abc'` would not be valid.


## Development

### Set up environment

```shell
git clone https://github.com/crate/cratedb-sqlparse

cd cratedb-sqlparse/cratedb_sqlparse_py

python3 -m venv .venv

source .venv/bin/activate

pip install --editable='.[develop,generate,release,test]'
```

Everytime you open a shell again you would need to run `source .venv/bin/activate`
to use `poe` commands.

### Run lint and tests with coverage.

```shell
poe check
```

### Run only tests

```shell
poe test
```

### Run a specific test.

```shell
poe test -k test_sqlparse_collects_exceptions_2
```

### Run linter

```shell
poe lint
```