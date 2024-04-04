import SqlBaseLexer from "./generated_parser/SqlBaseLexer.js";
import SqlBaseParser from "./generated_parser/SqlBaseParser.js";
import {CommonTokenStream, InputStream} from "antlr4";

export function sqlparse(query) {
    const input = new InputStream(query)
    const lexer = new SqlBaseLexer(input)
    // lexer.removeErrorListeners()
    const stream = new CommonTokenStream(lexer)

    const parser = new SqlBaseParser(stream)
    // parser.removeErrorListeners()
    // parser.addErrorListener(ExceptionErrorListener())

    const tree = parser.statements()
    return tree.children

}
