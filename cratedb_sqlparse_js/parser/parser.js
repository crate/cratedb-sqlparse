import SqlBaseLexer from "./generated_parser/SqlBaseLexer.js";
import SqlBaseParser from "./generated_parser/SqlBaseParser.js";
import {CommonTokenStream, ErrorListener, InputStream, Token} from "antlr4";

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

class ParsingError extends Error {}

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
        throw new ParsingError(`line${line}:${column} ${msg}`);
    }
}

export function sqlparse(query) {
    const input = new CaseInsensitiveStream(query);
    const lexer = new SqlBaseLexer(input);
    lexer.removeErrorListeners();
    const stream = new CommonTokenStream(lexer);

    const parser = new SqlBaseParser(stream);
    parser.removeErrorListeners();
    parser.addErrorListener(new ExceptionErrorListener());

    const tree = parser.statements();

    return tree.children;

}
