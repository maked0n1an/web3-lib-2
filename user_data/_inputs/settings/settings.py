from src._types.settings import DefaultSettings


settings: DefaultSettings = {
    'routes': [
        'layerzero-warmup',
    ],
    'show_execution': True,
    'dev_mode': False,
    'shuffle': {
        'wallets': True,
        'modules': True
    },
    'threads': 'all',
    'tx_attempts': 3,
    'delay': {
        'before_tx_receipt': (10, 20),
        'between_transactions': (10, 20),
        'between_modules': (10, 20)
    }
}