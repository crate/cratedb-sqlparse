import {sqlparse, ParsingError} from "../parser/parser.js";
import {expect, test} from 'vitest'

test('sqlparse parses one statement', () => {
    const ORIGINAL_QUERY = 'SELECT 1;'
    const queries = sqlparse(ORIGINAL_QUERY)
    expect(queries.length).toBe(1)

    const query = queries[0]
    expect(query.query).toBe(ORIGINAL_QUERY.replace(';', ''));
    expect(query.original_query).toBe(ORIGINAL_QUERY)
    expect(query.type).toBe('SELECT')
});

test('sqlparse parses several statements', () => {
    const ORIGINAL_QUERY = `    
    SELECT 1;
    INSERT INTO doc.tbl VALUES (1,2,3,4,5,6);
    DROP TABLE doc.tbl1`

    const queries = sqlparse(ORIGINAL_QUERY)
    expect(queries.length).toBe(3)

    expect(queries[0].type).toBe('SELECT')
    expect(queries[1].type).toBe('INSERT')
    expect(queries[2].type).toBe('DROP')
})

test('sqlparse supports dollar string', () => {
    const ORIGINAL_QUERY = "SELECT $$crate's performance$$"
    const query = sqlparse(ORIGINAL_QUERY)[0]
    expect(query.query).toBe(ORIGINAL_QUERY)
})

test('sqlparse raises ParsingError', ()=>{
    const ORIGINAL_QUERY = "some non sql string"
    expect(()=> sqlparse(ORIGINAL_QUERY)).toThrowError()
})

test('sqlparse is case insensitive', ()=>{
    const ORIGINAL_QUERY = 'inSerT InTo doc.Tbl1 Values (1)'
    const query = sqlparse(ORIGINAL_QUERY)
    expect(query[0].original_query).toBe(ORIGINAL_QUERY)
    expect(query[0].query).toBe(ORIGINAL_QUERY)
})