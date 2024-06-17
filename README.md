# cratedb-sqlparse

`Antlr4` is a parser generator for reading, processing and executing text, there are several
target languages (Java, Python, JavaScript, Dart) available. CrateDB uses the Java target.

The repository holds libraries/packages created from some of those available languages, so
far: `Python` and `JavaScript`. More might be added if needed in the future.

These libraries allow you to parse Crate's SQL dialect without sending it to a CrateDB instance.

- `Python`: https://github.com/crate/cratedb-sqlparse/tree/main/cratedb_sqlparse_py
- `Javascript`: https://github.com/crate/cratedb-sqlparse/tree/main/cratedb_sqlparse_js


## Install

You can install the package in both its Python and JavaScript variants.

- https://pypi.org/project/cratedb-sqlparse/
- https://www.npmjs.com/package/@cratedb/cratedb-sqlparse

### Python

```shell
pip install cratedb-sqlparse
```

### JavaScript
```shell
npm install @cratedb/cratedb-sqlparse
```


## Synopsis

```python
from cratedb_sqlparse import sqlparse

query = """
    SELECT * FROM SYS.SHARDS;
    INSERT INTO doc.tbl VALUES (1);
"""
statements = sqlparse(query)

select_query = statements[0]

print(select_query.query)
# 'SELECT * FROM SYS.SHARDS'
```

## Limitations

Listeners are not implemented, which means that you can only: Validate SQL syntax,
split queries and get some Tokens metadata from
the query, if you need some more information like what https://github.com/macbre/sql-metadata does (
e.g. get the columns of this query) open a new issue.

New features should preferably be implemented in all available targets.

## Adding a new target

The target language has to be available in antlr4,
see https://github.com/antlr/antlr4/blob/master/doc/targets.md.
 
Add the new target and paths to the build script, see `setup_grammar.py`.

There are several features that would need to be implemented, like case-insensitive input stream, native
exceptions as error listener, dollar-strings and any new one. See past commits to see how they were
implemented in Python and Javascript, remember that [CrateDB'S SQLParser](https://github.com/crate/crate/tree/master/libs/sql-parser/src/main/java/io/crate/sql/parser) written in Java is the most
complete and the default reference.

## Development

The generated parser is not uploaded to the repository because it is huge.
To use the package locally or to build a different version use the build script.
Further information can be found in the [developer guide](DEVELOP.md).
