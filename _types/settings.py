from dataclasses import dataclass
from enum import Enum

@dataclass
class Shuffle:
    wallets: bool
    modules: bool

class DefaultSettings:
    routes: list[str]
    shuffle: Shuffle

    threads: int
