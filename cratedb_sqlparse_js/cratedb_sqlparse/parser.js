import SqlBaseLexer from "./generated_parser/SqlBaseLexer.js";
import SqlBaseParser from "./generated_parser/SqlBaseParser.js";
import {CommonTokenStream, ErrorListener, InputStream, Interval, Token} from "antlr4";
import {AstBuilder} from "./AstBuilder.js";
import {Metadata} from "./models.js"
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

    constructor(query, msg, offending_token, e) {
        super(msg);
        this.query = query;
        this.msg = msg;
        this.offendingToken = offending_token;
        this.line = this.getLine();
        this.column = this.getColumn();
        this.errorMessage = this._getErrorMessage();
        this.errorMessageVerbose = this.getOriginalQueryWithErrorMarked()
    }

    _getErrorMessage() {
        return `[line ${this.line}:${this.column} ${this.message}]`
    }

    getColumn() {
        return this.offendingToken.column
    }

    getLine() {
        return this.offendingToken.line
    }

    getOriginalQueryWithErrorMarked() {
        const query = this.offendingToken.source[1].strdata
        const offendingTokenText = query.substring(this.offendingToken.start, this.offendingToken.stop + 1)
        const queryLines = query.split("\n")
        const offendingLine = queryLines[this.getLine() - 1]
        const newLineOffset = offendingLine.indexOf(offendingTokenText)

        const newline = (
            offendingLine
            + "\n"
            + (" ".repeat(newLineOffset) + "^".repeat(this.offendingToken.stop - this.offendingToken.start + 1))
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
    errors = []
    syntaxError(recognizer, offendingSymbol, line, column, msg, e) {
        throw new ParseError(
            e.ctx.parser.getTokenStream().getText(new Interval(
                e.ctx.start,
                e.offendingToken.tokenIndex)
            ),
            msg,
            offendingSymbol,
            e
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
            e.ctx.parser.getTokenStream().getText(new Interval(
                e.ctx.start,
                e.offendingToken.tokenIndex)
            ),
            msg,
            offendingSymbol,
            e
        )
        this.errors.push(error)
    }
}


/*
* Represents a CrateDB SQL statement.
* */
export class Statement {

    /**
     *
     * @property {String} query
     * @property {String} originalQuery
     * @property {Metadata} metadata
     * @property {String} type
     * @property {String} tree
     * @property {Object} ctx
     */
    constructor(ctx, exception) {
        this.query = ctx.parser.getTokenStream().getText(
            new Interval(
                ctx.start.tokenIndex,
                ctx.stop.tokenIndex,
            )
        )
        this.originalQuery = ctx.parser.getTokenStream().getText();
        this.tree = ctx.toStringTree(null, ctx.parser);
        this.type = ctx.start.text;
        this.ctx = ctx;
        this.exception = exception || null;
        this.metadata = new Metadata();
    }
}

function trim(string) {
    return string.replace(/^\s+|\s+$/gm, '');
}


function findSuitableError(statement, errors) {
    for (const error of errors) {
        let errorQuery = error.query;

        if (errorQuery.endsWith(";")) {
            errorQuery = errorQuery.substring(0, errorQuery.length - 1);
        }

        errorQuery = trim(errorQuery);

        // If a good match error_query contains statement.query
        if (statement.query.includes(errorQuery)) {
            statement.exception = error;
            errors.splice(errors.indexOf(error), 1);
        }
    }
}

/**
 *
 * @param {String} query
 * @param {Boolean} raise_exception
 * @returns {Statement[]}
 */
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
        statements.push(stmt)
    }

    const stmtEnricher = new AstBuilder()

    for (const stmt of statements) {
        stmtEnricher.enrich(stmt)
    }

    return statements
}