from enum import Enum
from typing import (
    Literal,
    TypeAlias,
    Tuple
)


# region Type aliases
IntRange: TypeAlias = Tuple[int, int]

HttpMethod: TypeAlias = Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH']


class strEnum(str, Enum):
    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

