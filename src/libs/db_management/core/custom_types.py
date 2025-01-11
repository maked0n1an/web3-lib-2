import json
from typing import (
    Annotated,
    List
)

from sqlalchemy import (
    TEXT,
    VARCHAR,
    String,
)
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import operators
from sqlalchemy.types import TypeDecorator


# region Annotated types
int_pk_an = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
str_10_an = Annotated[str, mapped_column(String(10))]
str_30_an = Annotated[str, mapped_column(String(30))]
str_42_unique_an = Annotated[str, mapped_column(String(42), unique=True)]
str_66_unique_an = Annotated[str, mapped_column(String(66), unique=True)]


class ArrayType(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value: List[str] | None, dialect):
        if value is not None:
            value = ','.join(value)
        return value

    def process_result_value(self, value: str | None, dialect):
        if value is not None:
            value = value.split(',')
        return value


array_or_none_an = Annotated[List[str] | None, mapped_column(ArrayType)]


class JSONEncodedDict(TypeDecorator):
    impl = VARCHAR
    cache_ok = True

    def coerce_compared_value(self, op, value):
        if op in (operators.like_op, operators.not_like_op):
            return String()
        else:
            return self

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
# endregion Annotated types
