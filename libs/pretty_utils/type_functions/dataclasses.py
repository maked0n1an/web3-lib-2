from dataclasses import dataclass
from typing import Union


@dataclass
class FromTo:
    from_: Union[int, float]
    to_: Union[int, float]