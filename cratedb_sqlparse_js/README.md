# CrateDB SQL Parser for JavaScript

![NPM License](https://img.shields.io/npm/l/@cratedb/cratedb-sqlparse)
![NPM Version](https://img.shields.io/npm/v/@cratedb/cratedb-sqlparse)
![NPM Downloads](https://img.shields.io/npm/dm/@cratedb/cratedb-sqlparse)

[![Tests](https://github.com/crate/cratedb-sqlparse/actions/workflows/javascript.yml/badge.svg)](https://github.com/crate/cratedb-sqlparse/actions/workflows/javascript.yml)

![NPM Unpacked Size](https://img.shields.io/npm/unpacked-size/@cratedb/cratedb-sqlparse)
![NPM Type Definitions](https://img.shields.io/npm/types/@cratedb/cratedb-sqlparse)


CrateDB SQL Parser for JavaScript, compiled from antlr4 JavaScript compile target.

### Simple usage
```javascript
import { sqlparse } from "@cratedb/cratedb-sqlparse";

const query = `
SELECT * FROM SYS.SHARDS;
INSERT INTO doc.tbl1 VALUES ('metric', 1238123, 'true');
`
const queries = sqlparse(query);

console.log(queries.length)
// 2

console.log(queries[0].query)
// SELECT * FROM SYS.SHARDS

console.log(queries[0].type)
// SELECT

console.log(queries[0].original_query)
// SELECT * FROM SYS.SHARDS;
// INSERT INTO doc.tbl1 VALUES ('metric', 1238123, 'true');
```

### CrateDB version
You can programmatically check the CrateDB version the package was compiled for in `index.js`

```javascript
import { __cratedb_version__ } from "@cratedb/cratedb-sqlparse";

console.log(__cratedb_version__)
// 5.6.4
```

### Features
Currently, we support the same features as CrateDB java's parser:
- First class CrateDB SQL dialect support.
- Input is case-insensitive.
- Native errors as exceptions.
- Dollar strings.

Optional features:

### Errors
Errors are thrown as 'ParseError' e.g.

```text
ParseError: line2:9 mismatched input 'ROM' expecting {<EOF>, ';'}
```
