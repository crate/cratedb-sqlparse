# Cratedb sqlparse - javascript edition.

![NPM License](https://img.shields.io/npm/l/cratedb-sqlparse?style=for-the-badge)
![NPM Version](https://img.shields.io/npm/v/cratedb-sqlparse?style=for-the-badge)
![NPM Unpacked Size](https://img.shields.io/npm/unpacked-size/cratedb-sqlparse?style=for-the-badge)
![NPM Type Definitions](https://img.shields.io/npm/types/cratedb-sqlparse?style=for-the-badge)

CrateDB sqlparser for javascript, compiled from antlr4 Javascript compile target.

### Simple usage
```javascript
import { sqlparse } from cratedb-sqlparse;

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
### Features
Currently, we support the same features as CrateDB java's parser:
- First class CrateDB sql dialect support.
- Input is case-insensitive.
- Native errors as exceptions.
- Dollar strings.

Optional features:

### Errors
Errors are thrown as 'ParseError' e.g:
```javascript
ParseError: line2:9 mismatched input 'ROM' expecting {<EOF>, ';'}
```