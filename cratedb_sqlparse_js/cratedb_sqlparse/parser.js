import SqlBaseLexer from "./generated_parser/SqlBaseLexer.js";
import SqlBaseParser from "./generated_parser/SqlBaseParser.js";
import {CommonTokenStream, ErrorListener, InputStream, Interval, Token} from "antlr4";

function BEGIN_DOLLAR_QUOTED_STRING_action(localctx, actionIndex) {
    if (actionIndex === 0) {
        this.tags.push(this.text);
    }
}

function END_DOLLAR_QUOTED_STRING_action(localctx, actionIndex) {
    if (actionIndex === 1) {
        this.tags.pop();
    }
}

function END_DOLLAR_QUOTED_STRING_sempred(localctx, predIndex) {
    if (predIndex === 0) {
        return this.tags[0] === this.text;
    }
}

SqlBaseLexer.prototype.tags = [];
SqlBaseLexer.prototype.BEGIN_DOLLAR_QUOTED_STRING_action = BEGIN_DOLLAR_QUOTED_STRING_action;
SqlBaseLexer.prototype.END_DOLLAR_QUOTED_STRING_action = END_DOLLAR_QUOTED_STRING_action;
SqlBaseLexer.prototype.END_DOLLAR_QUOTED_STRING_sempred = END_DOLLAR_QUOTED_STRING_sempred;

export class ParseError extends Error {
    name = 'ParseError'

    constructor(message, offending_token) {
        super(message);
        this.msg = message;
        this.offending_token = offending_token;
        this.line = this.getLine();
        this.column = this.getColumn();
        this.message = this.error_message();
    }

    error_message() {
        return `[line ${this.line}:${this.column} ${this.message}]`
    }

    getColumn() {
        return this.offending_token.column
    }

    getLine() {
        return this.offending_token.line
    }

    getOriginalQueryWithErrorMarked() {
        const query = this.offending_token.source[1].strdata
        const offendingTokenText = query.substring(this.offending_token.start, this.offending_token.stop + 1)
        const queryLines = query.split("\n")
        const offendingLine = queryLines[this.getLine() - 1]
        const newLineOffset = offendingLine.indexOf(offendingTokenText)

        const newline = (
            offendingLine
            + "\n"
            + ("‎".repeat(newLineOffset) + "^".repeat(this.offending_token.stop - this.offending_token.start + 1))
        )
        queryLines[this.line - 1] = newline

        return queryLines.join("\n")
    }
}

class CaseInsensitiveStream extends InputStream {
    LA(offset) {
        const result = super.LA(offset);
        if (result <= 0 || result === Token.EOF) {
            return result;
        }
        return String.fromCharCode(result).toUpperCase().charCodeAt(0);
    }
}

class ExceptionErrorListener extends ErrorListener {
    syntaxError(recognizer, offendingSymbol, line, column, msg, e) {
        throw new ParseError(
            msg,
            offendingSymbol,
            e,
            e.ctx.parser.getTokenStream().getText(e.ctx.start, e.offendingToken.tokenIndex)
        )
    }
}

class ExceptionCollectorListener extends ErrorListener {
    constructor() {
        super();
        this.errors = [];
    }

    syntaxError(recognizer, offendingSymbol, line, column, msg, e) {
        super.syntaxError(recognizer, offendingSymbol, line, column, msg, e);
        const error = new ParseError(
            msg,
            offendingSymbol,
            e,
            e.ctx.parser.getTokenStream().getText(e.ctx.start, e.offendingToken.tokenIndex)
        )
        this.errors.push(error)
    }
}

class Metadata {
    /*
    * Represents the metadata of the query, the actual interesting parts of the query such as:
    * table, schema, columns, options...
    */
    constructor(schema, table, parameterized_properties, with_properties) {
        this.schema = schema
        this.table = table
        this.parameterized_properties = parameterized_properties
        this.with_properties = with_properties
    }

    toString() {

    }
}

class Statement {
    /*
    * Represents a CrateDB SQL statement.
    * */
    constructor(ctx, exception) {
        this.query = ctx.parser.getTokenStream().getText(
            new Interval(
                ctx.start.tokenIndex,
                ctx.stop.tokenIndex,
            )
        )
        this.original_query = ctx.parser.getTokenStream().getText();
        this.tree = ctx.toStringTree(null, ctx.parser);
        this.type = ctx.start.text;
        this.ctx = ctx;
        self.exception = exception;
        self.metadata = new Metadata();
    }
}

function trim(string) {
    return string.replace(/^\s+|\s+$/gm, '');
}


function findSuitableError(statement, errors) {
    for (const error of errors) {
        let error_query = error.query;
        if (error_query.endsWith(";")) {
            error_query = error_query.substring(0, error_query.length - 1);
        }

        error_query = trim(error_query);

        // If a good match error_query contains statement.query
        if (error_query.contains(statement.query)) {
            statement.exception = error;
            errors.unshift(error);
        }
    }
}

export function sqlparse(query, raise_exception = false) {
    const input = new CaseInsensitiveStream(query);
    const lexer = new SqlBaseLexer(input);
    lexer.removeErrorListeners();
    const stream = new CommonTokenStream(lexer);

    const parser = new SqlBaseParser(stream);
    parser.removeErrorListeners();

    const errorListener = raise_exception ? new ExceptionErrorListener() : new ExceptionCollectorListener()
    parser.addErrorListener(errorListener);

    const tree = parser.statements();

    const statementsContext = tree.children.filter((children) => children instanceof SqlBaseParser.StatementContext)

    let statements = []
    for (const statementContext of statementsContext) {
        let stmt = new Statement(statementContext)
        findSuitableError(stmt, errorListener.errors)
    }
}