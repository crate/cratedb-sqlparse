import SqlBaseLexer from "./generated_parser/SqlBaseLexer.js";
import SqlBaseParser from "./generated_parser/SqlBaseParser.js";
import {CommonTokenStream, InputStream, Token} from "antlr4";

class CaseInsensitiveStream extends InputStream {
    LA(offset) {
        const result = super.LA(offset);
        if (result <= 0 || result === Token.EOF){
            return result;
        }
        return String.fromCharCode(result).toUpperCase().charCodeAt();
    }
}

export function sqlparse(query) {
    const input = new CaseInsensitiveStream(query);
    const lexer = new SqlBaseLexer(input);
    // lexer.removeErrorListeners()
    const stream = new CommonTokenStream(lexer);

    const parser = new SqlBaseParser(stream);
    // parser.removeErrorListeners()
    // parser.addErrorListener(ExceptionErrorListener())

    const tree = parser.statements();

    return tree.children;

}
