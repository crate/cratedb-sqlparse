import {expect, test} from 'vitest'
import {sqlparse} from "../cratedb_sqlparse/index.js";

test('sqlparse parses one statement', () => {
    const QUERY = 'SELECT 1;'
    const queries = sqlparse(QUERY)
    expect(queries.length).toBe(1)

    const stmts = queries[0]
    expect(stmts.query).toBe(QUERY.replace(';', ''));
    expect(stmts.originalQuery).toBe(QUERY)
    expect(stmts.type).toBe('SELECT')
});

test('sqlparse parses several statements', () => {
    const QUERY = `    
    SELECT 1;
    INSERT INTO doc.tbl VALUES (1,2,3,4,5,6);
    DROP TABLE doc.tbl1`

    const stmts = sqlparse(QUERY)

    expect(stmts.length).toBe(3)
    expect(stmts[0].type).toBe('SELECT')
    expect(stmts[1].type).toBe('INSERT')
    expect(stmts[2].type).toBe('DROP')
})

test('sqlparse supports dollar string', () => {
    const QUERY = "SELECT $$crate's performance$$"
    const stmts = sqlparse(QUERY)[0]
    expect(stmts.query).toBe(QUERY)
})

test('Test multiquery edge case', ()=>{
    // Test for https://github.com/crate/cratedb-sqlparse/issues/28,
    // if this ends up parsing 3 statements, we can change this test,
    // it's here, so we can programmatically track if the behavior changes.
    const QUERY = `
    SELECT A FROM tbl1 where ;
    SELEC 1;
    SELECT D, A FROM tbl1 WHERE;`

    const stmts = sqlparse(QUERY)
    expect(stmts.length).toBe(1)
})

test('sqlparse is case insensitive', ()=>{
    const QUERY = 'inSerT InTo doc.Tbl1 Values (1)'
    const stmts = sqlparse(QUERY)
    expect(stmts[0].originalQuery).toBe(QUERY)
    expect(stmts[0].query).toBe(QUERY)
})