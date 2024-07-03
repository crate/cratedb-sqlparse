import typing as t

from cratedb_sqlparse.generated_parser.SqlBaseParser import SqlBaseParser
from cratedb_sqlparse.generated_parser.SqlBaseParserVisitor import SqlBaseParserVisitor
from cratedb_sqlparse.models import Table


class AstBuilder(SqlBaseParserVisitor):
    """
    The class implements the antlr4 visitor pattern similar to how we do it in CrateDB
    https://github.com/crate/crate/blob/master/libs/sql-parser/src/main/java/io/crate/sql/parser/AstBuilder.java

    The biggest difference is that in CrateDB, `AstBuilder`, visitor methods
    return a specialized Statement visitor.

    Sqlparse just extracts whatever data it needs from the context and injects it to the current
    visited statement, enriching its metadata.
    """

    @property
    def stmt(self):
        if not hasattr(self, "_stmt"):
            raise Exception("You should call `enrich` first, that is the entrypoint.")
        return self._stmt

    @stmt.setter
    def stmt(self, value):
        self._stmt = value

    def enrich(self, stmt) -> None:
        self.stmt = stmt
        self.visit(self.stmt.ctx)

    def visitTableName(self, ctx: SqlBaseParser.TableNameContext):
        fqn = ctx.qname()
        parts = self.get_text(fqn).split(".")

        if len(parts) == 1:
            name = parts[0]
            schema = None
        else:
            schema, name = parts

        self.stmt.metadata.tables.append(Table(schema=schema, name=name))

    def visitGenericProperties(self, ctx: SqlBaseParser.GenericPropertiesContext):
        node_properties = ctx.genericProperty()

        properties = {}
        parameterized_properties = {}

        for property_ in node_properties:
            key = self.get_text(property_.ident())
            value = self.get_text(property_.expr())

            properties[key] = value

            if value and value[0] == "$":
                # It might be a parameterized value, e.g. '$1'
                if value[1:].isdigit():
                    parameterized_properties[key] = value

        self.stmt.metadata.with_properties = properties
        self.stmt.metadata.parameterized_properties = parameterized_properties

    def get_text(self, node) -> t.Optional[str]:
        """Gets the text representation of the node or None if it doesn't have one"""
        if node:
            return node.getText().replace("'", "").replace('"', "")
        return node
