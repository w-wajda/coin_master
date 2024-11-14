import json

import sqlalchemy as sa
from sqlalchemy.types import (
    ARRAY,
    TypeDecorator,
)


class JSONArray(TypeDecorator):
    impl = sa.Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)


class Array(TypeDecorator):
    impl = sa.Text

    def __init__(self, item_type, as_tuple=False, dimensions=1, **kwargs):
        super().__init__(**kwargs)
        self.item_type = item_type
        self.as_tuple = as_tuple
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        if dialect.name == "sqlite":
            return JSONArray()
        elif dialect.name == "postgresql":
            return ARRAY(self.item_type, dimensions=self.dimensions, as_tuple=self.as_tuple)
        else:
            raise NotImplementedError(f"Dialect '{dialect.name}' is not supported")

    def process_bind_param(self, value, dialect):
        if dialect.name == "sqlite":
            return JSONArray().process_bind_param(value, dialect)
        elif dialect.name == "postgresql":
            return value
        else:
            raise NotImplementedError(f"Dialect '{dialect.name}' is not supported")

    def process_result_value(self, value, dialect):
        if dialect.name == "sqlite":
            return JSONArray().process_result_value(value, dialect)
        elif dialect.name == "postgresql":
            return value
        else:
            raise NotImplementedError(f"Dialect '{dialect.name}' is not supported")
