from dataclasses import dataclass


@dataclass
class Shuffle:
    wallets: bool
    modules: bool


class DefaultSettings:
    routes: list[str]
    shuffle: Shuffle

    threads: int
