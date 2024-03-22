from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from cratedb_sqlparse.parser.generated_parser.SqlBaseParser import SqlBaseParser
from cratedb_sqlparse.parser.generated_parser.SqlBaseLexer import SqlBaseLexer


def BEGIN_DOLLAR_QUOTED_STRING_action(self, localctx, actionIndex):
    if actionIndex == 0:
        self.tags.append(self.text)


def END_DOLLAR_QUOTED_STRING_action(self, localctx, actionIndex):
    if actionIndex == 1:
        self.tags.pop()


def END_DOLLAR_QUOTED_STRING_sempred(self, localctx, predIndex):
    if predIndex == 0:
        return self.tags[0] == self.text


SqlBaseLexer.tags = []
SqlBaseLexer.BEGIN_DOLLAR_QUOTED_STRING_action = BEGIN_DOLLAR_QUOTED_STRING_action
SqlBaseLexer.END_DOLLAR_QUOTED_STRING_action = END_DOLLAR_QUOTED_STRING_action
SqlBaseLexer.END_DOLLAR_QUOTED_STRING_sempred = END_DOLLAR_QUOTED_STRING_sempred


class ParsingException(Exception):
    pass


class CaseInsensitiveStream(InputStream):
    def LA(self, offset: int):
        result = super().LA(offset)
        if result <= 0 or result == 59:  # 59 -> ;
            return result
        return ord(chr(result).upper())


class ExceptionErrorListener(ErrorListener):
    """
    Error listener that raises the antlr4 error as a Python exception.
    """

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ParsingException(f'line{line}:{column} {msg}')


class Statement:
    """
    Represents a CrateDB SQL statement.
    """

    def __init__(self, ctx: SqlBaseParser.StatementContext):
        self.ctx: SqlBaseParser.StatementContext = ctx

    @property
    def tree(self):
        return self.ctx.toStringTree(recog=self.ctx.parser)

    @property
    def original_query(self):
        return self.ctx.parser.getTokenStream().getText()

    @property
    def query(self) -> str:
        """
        Returns the query, comments and ';' are not included.
        """
        return self.ctx.parser.getTokenStream().getText(
            start=self.ctx.start.tokenIndex,
            stop=self.ctx.stop.tokenIndex
        )

    @property
    def type(self):
        """
        Returns the type of the Statement, i.e.: 'SELECT, 'UPDATE', 'COPY TO'...
        """
        return self.ctx.start.text

    def __repr__(self):
        return f'{self.__class__.__qualname__}<{self.query if len(self.query) < 15 else self.query[:15] + "..."}>'


def sqlparse(query: str) -> list[Statement]:
    """
    Parses a string into SQL `Statement`.
    """
    input = CaseInsensitiveStream(query)
    lexer = SqlBaseLexer(input)
    lexer.removeErrorListeners()
    stream = CommonTokenStream(lexer)

    parser = SqlBaseParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(ExceptionErrorListener())

    tree = parser.statements()

    # At this point, all errors are already raised; it's seasonably safe to assume
    # that the statements are valid.
    statements = list(filter(
        lambda children: isinstance(children, SqlBaseParser.StatementContext), tree.children
    ))

    return [Statement(statement) for statement in statements]
