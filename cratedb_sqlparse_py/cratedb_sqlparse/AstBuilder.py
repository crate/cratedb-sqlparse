import typing as t

from cratedb_sqlparse.generated_parser.SqlBaseParser import SqlBaseParser
from cratedb_sqlparse.generated_parser.SqlBaseParserVisitor import SqlBaseParserVisitor


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
        parts = self.get_text(fqn).replace('"', "").split(".")

        if len(parts) == 1:
            name = parts[0]
            schema = None
        else:
            schema, name = parts

        self.stmt.metadata.table_name = name
        self.stmt.metadata.schema = schema

    def visitGenericProperties(self, ctx: SqlBaseParser.GenericPropertiesContext):
        node_properties = ctx.genericProperty()

        properties = {}
        interpolated_properties = {}

        for property in node_properties:
            key = self.get_text(property.ident())
            value = self.get_text(property.expr())

            properties[key] = value

            if value[0] == "$":
                # It might be a interpolated value, e.g. '$1'
                if value[1:].isdigit():
                    interpolated_properties[key] = value

        self.stmt.metadata.with_properties = properties
        self.stmt.metadata.interpolated_properties = interpolated_properties

    def get_text(self, node) -> t.Optional[str]:
        """Gets the text representation of the node or None if it doesn't have one"""
        if node:
            return node.getText()
        return node
