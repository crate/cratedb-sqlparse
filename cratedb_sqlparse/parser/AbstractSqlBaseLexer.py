from antlr4 import Lexer


class AbstractSqlBaseLexer(Lexer):
    """
    antlr4 generates this class we added in CrateDB (https://github.com/crate/crate/commit/8e7cfd7c4a05fc27de8ce71af9165b98c986d883)
    in order to implement $ strings, ie: "SELECT $my friend's house$", we cannot do the same since it also generates invalid syntax:

    # SqlBaseLexer.py
    class SqlBaseLexer(AbstractSqlBaseLexer):
        ...


        def END_DOLLAR_QUOTED_STRING_sempred(...):
            if actionIndex == 1:
                pushTags()

                ^^^^^^^^^

    #

    pushTags here is valid Java syntax but wrong Python syntax, we patch this in parser.py.
    """

    pass
