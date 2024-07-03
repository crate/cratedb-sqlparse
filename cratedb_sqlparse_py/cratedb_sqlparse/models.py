import dataclasses
from typing import List


def quote(text: str, quote_with: str = '"') -> str:
    return quote_with + text + quote_with


@dataclasses.dataclass
class Table:
    name: str
    schema: str = None

    @property
    def fqn(self) -> str:
        return (quote(self.schema) + "." if self.schema else "") + quote(self.name)


@dataclasses.dataclass
class Metadata:
    """
    Represents the metadata of the query, the actual interesting parts of the query such as:
    table, schema, columns, options...
    """

    tables: List[Table] = dataclasses.field(default_factory=list)
    parameterized_properties: dict = dataclasses.field(default_factory=dict)
    with_properties: dict = dataclasses.field(default_factory=dict)
