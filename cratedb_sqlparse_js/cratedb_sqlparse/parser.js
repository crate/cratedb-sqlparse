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

    /**
     *
     * @param {string} query
     * @param {string} msg
     * @param {object} offending_token
     * @param {object} e
     * @member {string} errorMessage
     * @member {string} errorMessageVerbose
     */
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

    /**
     *
     * @returns {Number}
     */
    getColumn() {
        return this.offendingToken.column
    }

    /**
     *
     * @returns {Number}
     */
    getLine() {
        return this.offendingToken.line
    }

    /**
     *
     * @returns {string}
     */
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
     * @member {Statement} query
     * @member {string} originalQuery
     * @member {Metadata} metadata
     * @member {string} type - The type of query, example: 'SELECT'
     * @member {string} tree
     * @param {object} ctx
     * @param {ParseError} exception
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

/**
 *
 * @param {string} string
 * @returns {string}
 */
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
        if (errorQuery.includes(statement.query)) {
            statement.exception = error;
            errors.splice(errors.indexOf(error), 1);
        }
    }
}

/**
 *
 * @param {string} query
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

        if (statementsContext.length === 1 && errorListener.errors) {
            stmt.exception = errorListener.errors.pop();

        } else {
            findSuitableError(stmt, errorListener.errors)
        }

        statements.push(stmt)
    }

    if (errorListener.errors.length === 1) {
        // Fixme, what if there are two unassigned errors ?
        // can that even be possible?
        let error = errorListener.errors[0]

        for (const stmt of statements) {
            if (stmt.exception === null && stmt.query.includes(error.query)) {
                stmt.exception = error
                break;
            }
        }
    }

    if (errorListener.errors.length > 1) {
        console.error("Could not match errors to queries, too much ambiguity, please report it opening an issue with the query.")
    }


    const stmtEnricher = new AstBuilder()

    for (const stmt of statements) {
        stmtEnricher.enrich(stmt)
    }

    return statements
}