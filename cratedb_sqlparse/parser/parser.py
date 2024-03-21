from antlr4 import InputStream, CommonTokenStream
from cratedb_sqlparse.parser.SqlBaseParser import SqlBaseParser
from cratedb_sqlparse.parser.SqlBaseLexer import SqlBaseLexer


class CaseInsensitiveStream(InputStream):
    def LA(self, offset: int):
        result = super().LA(offset)
        if result <= 0 or result == 59:  # 59 -> ;
            return result
        return ord(chr(result).upper())


class Statement:
    def __init__(self, ctx: SqlBaseParser.StatementsContext, stream, parser):
        self.ctx = ctx
        self.stream = stream
        self.parser = parser

    @property
    def tree(self):
        return self.ctx.toStringTree(recog=self.parser)

    @property
    def original_query(self):
        return self.stream.getText()

    @property
    def query(self):
        return self.stream.getText(
            start=self.ctx.start.tokenIndex,
            stop=self.ctx.stop.tokenIndex
        )

    @property
    def type(self):
        return self.ctx.start.text

    def __repr__(self):
        return f'{self.__class__.__qualname__}<{self.query}>'


def sqlparse(query: str) -> list[Statement]:
    input = CaseInsensitiveStream(query)
    lexer = SqlBaseLexer(input)
    stream = CommonTokenStream(lexer)
    parser = SqlBaseParser(stream)
    tree = parser.statements()

    # Fixme: We lose the message of the exception when we raise it.
    for statement in tree.children:
        if hasattr(statement, 'exception') and statement.exception is not None:
            raise statement.exception

    statements = list(filter(
        lambda children: isinstance(children, SqlBaseParser.StatementContext), tree.children
    ))

    return [Statement(statement, stream, parser) for statement in statements]
