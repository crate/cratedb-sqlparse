from typing import List

from antlr4 import CommonTokenStream, InputStream, RecognitionException, Token
from antlr4.error.ErrorListener import ErrorListener

from cratedb_sqlparse.AstBuilder import AstBuilder
from cratedb_sqlparse.generated_parser.SqlBaseLexer import SqlBaseLexer
from cratedb_sqlparse.generated_parser.SqlBaseParser import SqlBaseParser
from cratedb_sqlparse.models import Metadata


def BEGIN_DOLLAR_QUOTED_STRING_action(self, localctx, actionIndex):
    if actionIndex == 0:
        self.tags.append(self.text)


def END_DOLLAR_QUOTED_STRING_action(self, localctx, actionIndex):
    if actionIndex == 1:
        self.tags.pop()


def END_DOLLAR_QUOTED_STRING_sempred(self, localctx, predIndex) -> bool:
    if predIndex == 0:
        return self.tags[0] == self.text
    return False


SqlBaseLexer.tags = []
SqlBaseLexer.BEGIN_DOLLAR_QUOTED_STRING_action = BEGIN_DOLLAR_QUOTED_STRING_action
SqlBaseLexer.END_DOLLAR_QUOTED_STRING_action = END_DOLLAR_QUOTED_STRING_action
SqlBaseLexer.END_DOLLAR_QUOTED_STRING_sempred = END_DOLLAR_QUOTED_STRING_sempred


class ParsingException(Exception):
    def __init__(self, *, query: str, msg: str, offending_token: Token, e: RecognitionException):
        self.message = msg
        self.offending_token = offending_token
        self.e = e
        self.query = query

    @property
    def error_message(self):
        return f"{self!r}[line {self.line}:{self.column} {self.message}]"

    @property
    def original_query_with_error_marked(self):
        query = self.offending_token.source[1].strdata
        offending_token_text: str = query[self.offending_token.start : self.offending_token.stop + 1]
        query_lines: list = query.split("\n")
        offending_line: str = query_lines[self.line - 1]

        # White spaces from the beginning of the offending line to the offending text, so the '^'
        # chars are correctly placed below the offending token.
        newline_offset = offending_line.index(offending_token_text)
        newline = (
            offending_line
            + "\n"
            + (" " * newline_offset + "^" * (self.offending_token.stop - self.offending_token.start + 1))
        )

        query_lines[self.line - 1] = newline

        msg = "\n".join(query_lines)
        return msg

    @property
    def column(self):
        return self.offending_token.column

    @property
    def line(self):
        return self.offending_token.line

    def __repr__(self):
        return type(self.e).__qualname__

    def __str__(self):
        return self.error_message


class CaseInsensitiveStream(InputStream):
    def LA(self, offset: int):
        result = super().LA(offset)
        if result <= 0 or result == Token.EOF:
            return result
        return ord(chr(result).upper())


class ExceptionErrorListener(ErrorListener):
    """
    Error listener that raises the antlr4 error as a Python exception.
    """

    errors = ()  # Dummy for passing tests, should not be used.

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error = ParsingException(
            msg=msg,
            offending_token=offendingSymbol,
            e=e,
            query=e.ctx.parser.getTokenStream().getText(e.ctx.start, e.offendingToken.tokenIndex),
        )
        raise error


class ExceptionCollectorListener(ErrorListener):
    """
    Error listener that collects all errors into errors for further processing.

    Based partially on https://github.com/antlr/antlr4/issues/396
    """

    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error = ParsingException(
            msg=msg,
            offending_token=offendingSymbol,
            e=e,
            query=e.ctx.parser.getTokenStream().getText(e.ctx.start, e.offendingToken.tokenIndex),
        )

        self.errors.append(error)


class Statement:
    """
    Represents a CrateDB SQL statement.
    """

    def __init__(self, ctx: SqlBaseParser.StatementContext, exception: ParsingException = None):
        self.ctx: SqlBaseParser.StatementContext = ctx
        self.exception = exception
        self.metadata = Metadata()

    @property
    def tree(self):
        """
        Returns the String representation of the Tree in LISP format.
        """
        return self.ctx.toStringTree(recog=self.ctx.parser)

    @property
    def original_query(self):
        """
        The original query that was fed into `sqlparse`, including semicolons and comments.
        """
        return self.ctx.parser.getTokenStream().getText()

    @property
    def query(self) -> str:
        """
        Returns the query, comments and ';' are not included.
        """
        return self.ctx.parser.getTokenStream().getText(start=self.ctx.start, stop=self.ctx.stop)

    @property
    def type(self):
        """
        Returns the type of the Statement, i.e.: 'SELECT, 'UPDATE', 'COPY TO'...
        """
        return self.ctx.start.text

    def __repr__(self):
        return f'{self.__class__.__qualname__}<{self.query if len(self.query) < 15 else self.query[:15] + "..."}>'


def find_suitable_error(statement, errors):
    for error in errors[:]:
        # We clean the error_query of ';' and spaces because ironically,
        # we can get the full query in the error but not in the parsed statement.
        error_query = error.query
        if error_query.endswith(";"):
            error_query = error_query[: len(error_query) - 1]

        error_query = error_query.lstrip().rstrip()

        # If a good match error_query contains statement.query
        if statement.query in error_query:
            statement.exception = error
            errors.pop(errors.index(error))


def sqlparse(query: str, raise_exception: bool = False) -> List[Statement]:
    """
    Parses a string into SQL `Statement`.
    """
    input_ = CaseInsensitiveStream(query)
    lexer = SqlBaseLexer(input_)
    lexer.removeErrorListeners()
    stream = CommonTokenStream(lexer)

    parser = SqlBaseParser(stream)
    parser.removeErrorListeners()
    error_listener = ExceptionErrorListener() if raise_exception else ExceptionCollectorListener()
    parser.addErrorListener(error_listener)

    tree = parser.statements()

    statements_context: list[SqlBaseParser.StatementContext] = list(
        filter(lambda children: isinstance(children, SqlBaseParser.StatementContext), tree.children)
    )

    statements = []

    for statement_context in statements_context:
        stmt = Statement(statement_context)
        if len(statements_context) == 1 and error_listener.errors:
            # There is only one statement parsed, no need to get fancy to match.
            stmt.exception = error_listener.errors.pop()

        else:
            find_suitable_error(stmt, error_listener.errors)

        statements.append(stmt)

    else:
        # We might still have error(s) that we couldn't match with their origin statement,
        # this happens when the query is composed of only one keyword, e.g. 'SELCT 1'
        # the error.query will be 'SELCT' instead of 'SELCT 1'.
        if len(error_listener.errors) == 1:
            # This case has an edge case where we hypothetically assign the
            # wrong error to a statement, for example,
            #     SELECT A FROM tbl1;
            #     SELEC 1;
            #          ^
            # This would match both conditionals, this however, is protected
            # by https://github.com/crate/cratedb-sqlparse/issues/28, but might
            # change in the future.
            error = error_listener.errors[0]
            for stmt in statements:
                if stmt.exception is None and error.query in stmt.query:
                    stmt.exception = error
                    break

        if len(error_listener.errors) > 1:
            # We might have too much ambiguity to match errors, but also one statement can
            # generate several exceptions, and we only support one per statement so this could be
            # triggered and not be an actual error.
            pass

    # We extract the metadata and enrich every Statement's `metadata`.
    stmt_enricher = AstBuilder()

    for stmt in statements:
        stmt_enricher.enrich(stmt)

    return statements
