from typing import (
    Literal,
    TypedDict,
    Union
)

from src._types.common import IntRange


Route = Literal[
    'layerzero-warmup',
    'cex-top-up'
]
Module = Literal[
    'stargate',
    'coredao-bridge',
    'testnet-bridge',
]


class DelaySettings(TypedDict):
    before_tx_receipt: IntRange
    between_transactions: IntRange
    between_modules: IntRange


class ShuffleSettings(TypedDict):
    wallets: bool
    modules: bool


class DefaultSettings(TypedDict):
    routes: list[Route]

    show_execution: bool
    dev_mode: bool

    shuffle: ShuffleSettings
    threads: Union[int, Literal['all']]
    tx_attempts: int
    delay: DelaySettings


default_settings: DefaultSettings = {
    'routes': [
        'layerzero-warmup', 
    ],
    'shuffle': {
        'wallets': True, 
        'modules': True
    },
    'show_execution': True,
    'dev_mode': True,
    
    'threads': 'all',
    'tx_attempts': 1,
    'delay': {
        'before_tx_receipt': (1, 10),
        'between_transactions': (1, 10),
        'between_modules': (1, 10)
    }
}