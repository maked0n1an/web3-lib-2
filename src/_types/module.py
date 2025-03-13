from typing import TypedDict

from src._types.common import IntRange


class DefaultModuleSettings(TypedDict):
    count: IntRange
    index_group: int
