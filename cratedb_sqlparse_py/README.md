# CrateDB SQL Parser for Python

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

sqlparse('SUUULECT * FROM sys.shards')
# cratedb_sqlparse.parser.parser.ParsingException: line1:0 mismatched input 'SUUULECT' expecting {'SELECT', 'DEALLOCATE', ...}
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
