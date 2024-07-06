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
import {sqlparse} from "@cratedb/cratedb-sqlparse";

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
import {__cratedb_version__} from "@cratedb/cratedb-sqlparse";

console.log(__cratedb_version__)
// 5.7.2
```

### Features

Currently, the parser supports a subset of the features of CrateDB's Java/ANTLR parser:

- First class CrateDB SQL dialect support.
- Input is case-insensitive.
- Native errors as exceptions or as objects.
- Dollar strings.
- Tables
- Properties and parametrized properties.

### Exceptions and errors.

By default, exceptions are stored in `statement.exception`.

```javascript
import {sqlparse} from "@cratedb/cratedb-sqlparse";

const query = `
SELECT COUNT(*) FROM doc.tbl f HERE f.id = 1;

INSERT INTO doc.tbl VALUES (1, 23, 4);
`
const statements = sqlparse(query)
const stmt = statements[0]

if (stmt.exception) {
    console.log(stmt.exception.errorMessage)
    // [line 2:43 mismatched input 'HERE' expecting {<EOF>, ';'}]

    console.log(stmt.exception.errorMessageVerbose)
    //      SELECT COUNT(*) FROM doc.tbl f HERE f.id = 1;
    //                                     ^^^^
    //      INSERT INTO doc.tbl VALUES (1, 23, 4);
}

console.log(stmt.exception)

// ParseError: mismatched input 'HERE' expecting {<EOF>, ';'}
//     at ExceptionCollectorListener.syntaxError (file:///home/surister/PycharmProjects/cratedb-sqlparse/cratedb_sqlparse_js/cratedb_sqlparse/parser.js:115:23)
//     at file:///home/surister/PycharmProjects/cratedb-sqlparse/cratedb_sqlparse_js/node_modules/antlr4/dist/antlr4.node.mjs:1:42125
//     at Array.map (<anonymous>)
//     at wt.syntaxError (file:///home/surister/PycharmProjects/cratedb-sqlparse/cratedb_sqlparse_js/node_modules/antlr4/dist/antlr4.node.mjs:1:42115)
//     at SqlBaseParser.notifyErrorListeners (file:///home/surister/PycharmProjects/cratedb-sqlparse/cratedb_sqlparse_js/node_modules/antlr4/dist/antlr4.node.mjs:1:102085)
//     at Ce.reportInputMismatch (file:///home/surister/PycharmProjects/cratedb-sqlparse/cratedb_sqlparse_js/node_modules/antlr4/dist/antlr4.node.mjs:1:90577)
//     at Ce.reportError (file:///home/surister/PycharmProjects/cratedb-sqlparse/cratedb_sqlparse_js/node_modules/antlr4/dist/antlr4.node.mjs:1:88813)
//     at SqlBaseParser.statements (file:///home/surister/PycharmProjects/cratedb-sqlparse/cratedb_sqlparse_js/cratedb_sqlparse/generated_parser/SqlBaseParser.js:1345:28)
//     at sqlparse (file:///home/surister/PycharmProjects/cratedb-sqlparse/cratedb_sqlparse_js/cratedb_sqlparse/parser.js:207:25)
//     at file:///home/surister/PycharmProjects/cratedb-sqlparse/cratedb_sqlparse_js/t.js:4:14 {
//   query: 'SELECT COUNT(*) FROM doc.tbl f HERE',
//   msg: "mismatched input 'HERE' expecting {<EOF>, ';'}",
//   offendingToken: bt {
//     source: [ [SqlBaseLexer], [CaseInsensitiveStream] ],
//     type: 322,
//     channel: 0,
//     start: 32,
//     stop: 35,
//     tokenIndex: 16,
//     line: 2,
//     column: 31,
//     _text: null
//   },
//   line: 2,
//   column: 31,
//   errorMessage: "[line 2:31 mismatched input 'HERE' expecting {<EOF>, ';'}]",
//   errorMessageVerbose: '\n' +
//     'SELECT COUNT(*) FROM doc.tbl f HERE f.id = 1;\n' +
//     '                               ^^^^\n' +
//     '\n' +
//     'INSERT INTO doc.tbl VALUES (1, 23, 4);\n'
// }
```

In some situations, you might want sqlparse to throw an error.

You can set `raise_exception` to `true`

```javascript
import {sqlparse} from "@cratedb/cratedb-sqlparse";

let stmt = sqlparse('SELECT COUNT(*) FROM doc.tbl f WHERE .id = 1;', true);

//         throw new ParseError(
//            ^
//
// ParseError: no viable alternative at input 'SELECT COUNT(*) FROM doc.tbl f WHERE .'
```

Catch the exception:

```javascript
import {sqlparse} from "@cratedb/cratedb-sqlparse";

try {
    sqlparse('SELECT COUNT(*) FROM doc.tbl f WHERE .id = 1;', true)
} catch (e) {
    console.log(e)
}
```

> [!NOTE]
> It will only raise the first exception it finds, even if you pass in several statements.

### Query metadata

Query metadata can be read with `statement.metadata`

```javascript
import {sqlparse} from "@cratedb/cratedb-sqlparse";

const stmt = sqlparse("SELECT A, B FROM doc.tbl12")[0]

console.log(stmt.metadata);

// Metadata {
//   tables: [ Table { name: 'tbl12', schema: 'doc' } ],
//   parameterizedProperties: {},
//   withProperties: {}
// }

```

#### Query properties

Properties defined within a `WITH` statement, `statement.metadata.withProperties:`.

```javascript
import {sqlparse} from "@cratedb/cratedb-sqlparse";


const stmt = sqlparse(`
    CREATE TABLE doc.tbl12 (A TEXT) WITH (
      "allocation.max_retries" = 5,
      "blocks.metadata" = false
    );
`)[0]

console.log(stmt.metadata);

// Metadata {
//   tables: [ Table { name: 'tbl12', schema: 'doc' } ],
//   parameterizedProperties: {},
//   withProperties: { 'allocation.max_retries': '5', 'blocks.metadata': 'false' }
// }
```

#### Table name
```javascript
console.log(stmt.metadata.tables)
// [ Table { name: 'tbl12', schema: 'doc' } ]

table = stmt.metadata.tables[0]

console.log(table.schema, table.name, table.fqn)
// doc tbl12 "doc"."tbl12"
```

#### Parameterized properties

Parameterized properties are properties without a real defined value, marked with a dollar string,  `metadata.parameterized_properties`

```javascript
import {sqlparse} from "@cratedb/cratedb-sqlparse";

const stmt = sqlparse(`
    CREATE TABLE doc.tbl12 (A TEXT) WITH (
    "allocation.max_retries" = 5,
    "blocks.metadata" = $1
);
`)[0]

console.log(stmt.metadata)

// Metadata {
//   tables: [ Table { name: 'tbl12', schema: 'doc', fqn: '"doc"."tbl12"' } ],
//   parameterizedProperties: { 'blocks.metadata': '$1' },
//   withProperties: { 'allocation.max_retries': '5', 'blocks.metadata': '$1' }
// }
```

In this case, `blocks.metadata` will be in `with_properties` and `parameterized_properties` as well.

For values to be picked up they need to start with a dollar `'$'` and be preceded by integers, e.g. `'$1'` or `'$123'`.
`'$123abc'` would not be valid.