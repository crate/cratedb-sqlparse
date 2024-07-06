import {expect, test} from 'vitest'
import {sqlparse} from "../cratedb_sqlparse/index.js";
import {Metadata} from "../cratedb_sqlparse/models.js";

test('Statement has metadata', () => {
    const query = "SELECT 1; SELECT 2;"
    const stmts = sqlparse(query);

    for (const stmt of stmts) {
        expect(stmt.metadata).not.toBeNull
        expect(stmt.metadata).toBeInstanceOf(Metadata)
    }
})

test("Statement's metadata has Tables", () => {
    const query = "SELECT _ FROM a.b, d"
    const stmt = sqlparse(query)[0]

    expect(stmt.metadata.tables).not.toBeNull
    expect(stmt.metadata.tables[0].schema).toBe('a')
    expect(stmt.metadata.tables[0].name).toBe('b')
    expect(stmt.metadata.tables[0].fqn).toBe('"a"."b"')

    expect(stmt.metadata.tables[1].schema).toBeNull()
    expect(stmt.metadata.tables[1].name).toBe('d')
    expect(stmt.metadata.tables[1].fqn).toBe('"d"')
})

test("Statement's metadata correctly gets parameterized properties", ()=>{
    const query = "CREATE TABLE tbl (A TEXT) WITH ('key' = $1, 'key2' = '$2')"
    const stmt = sqlparse(query)[0]
    const expected = { key: '$1', key2: '$2' }

    expect(stmt.metadata.withProperties).toStrictEqual(expected)
    expect(stmt.metadata.parameterizedProperties).toStrictEqual(expected)
})

test("Statement's metadata correctly gets with properties", () => {
    const query = "CREATE TABLE tbl (A TEXT) WITH ('key' = 'val', 'key2' = 2, 'key3' = true)"
    const stmt = sqlparse(query)[0]
    const expected = {key: 'val', key2: '2', key3: 'true'}

    expect(stmt.metadata.withProperties).toStrictEqual(expected)
    expect(stmt.metadata.parameterizedProperties).toStrictEqual({})
})
