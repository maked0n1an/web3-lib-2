from enum import Enum

from src.libs.async_eth_lib.utils.helpers import read_json
from src._types.networks import NetworkNames
from src._types.tokens import TokenSymbol
from src.tasks._common.utils import StandardSettings
from user_data._inputs.settings._global import MODULES_SETTINGS_FILE_PATH

# region Settings
class CoreDaoBridgeSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)

        self.bridge = StandardSettings(
            settings=settings,
            module_name='coredao',
            action_name='bridge'
        )
# endregion Settings


class CoreDaoBridgeABIs:
    TO_CORE_BRIDGE_ABI =    ('src', 'data', 'abis', 'coredao', 'to_core_bridge_abi.json')
    FROM_CORE_BRIDGE_ABI =  ('src', 'data', 'abis', 'coredao', 'from_core_bridge_abi.json')


class CoreDaoBridgeData:
    def __init__(self):
        self.contracts = {
            NetworkNames.Arbitrum: {
                TokenSymbol.USDT: '0x29d096cD18C0dA7500295f082da73316d704031A',
                TokenSymbol.USDC: '0x29d096cD18C0dA7500295f082da73316d704031A',
            },
            NetworkNames.Avalanche: {
                TokenSymbol.USDT: '0x29d096cD18C0dA7500295f082da73316d704031A',
                TokenSymbol.USDC: '0x29d096cD18C0dA7500295f082da73316d704031A',
            },
            NetworkNames.BSC: {
                TokenSymbol.USDT: '0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
                TokenSymbol.USDC: '0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
            },
            NetworkNames.Core: {
                TokenSymbol.USDT: '0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE',
                TokenSymbol.USDC: '0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE',
            },
            NetworkNames.Optimism: {
                TokenSymbol.USDT: '0x29d096cD18C0dA7500295f082da73316d704031A',
                TokenSymbol.USDC: '0x29d096cD18C0dA7500295f082da73316d704031A',
            },
            NetworkNames.Polygon: {
                TokenSymbol.USDT: '0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
                TokenSymbol.USDC: '0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
            }
        }

def get_coredao_bridge_routes(
) -> dict[NetworkNames, dict[TokenSymbol, list[tuple[NetworkNames, TokenSymbol]]]]:
    return {
        NetworkNames.Arbitrum: {
            TokenSymbol.USDT: [
                (NetworkNames.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Core, TokenSymbol.USDC)
            ]
        },
        NetworkNames.Avalanche: {
            TokenSymbol.USDT: [
                (NetworkNames.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Core, TokenSymbol.USDC)
            ]
        },
        NetworkNames.BSC: {
            TokenSymbol.USDT: [
                (NetworkNames.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Core, TokenSymbol.USDC)
            ]
        },
        NetworkNames.Optimism: {
            TokenSymbol.USDT: [
                (NetworkNames.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Core, TokenSymbol.USDC)
            ]
        },
        NetworkNames.Polygon: {
            TokenSymbol.USDT: [
                (NetworkNames.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Core, TokenSymbol.USDC)
            ]
        },
        NetworkNames.Core: {
            TokenSymbol.USDT: [
                (NetworkNames.Arbitrum,     TokenSymbol.USDT),
                (NetworkNames.Avalanche,    TokenSymbol.USDT),
                (NetworkNames.BSC,          TokenSymbol.USDT),
                (NetworkNames.Optimism,     TokenSymbol.USDT),
                (NetworkNames.Polygon,      TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Arbitrum,     TokenSymbol.USDC),
                (NetworkNames.Avalanche,    TokenSymbol.USDC),
                (NetworkNames.BSC,          TokenSymbol.USDC),
                (NetworkNames.Optimism,     TokenSymbol.USDC),
                (NetworkNames.Polygon,      TokenSymbol.USDC),
            ],
        }
    }


L0_IDS = {
    'v1': {
        NetworkNames.Ethereum: 101,
        NetworkNames.Arbitrum: 110,
        NetworkNames.Avalanche: 103,
        NetworkNames.Base: 184,
        NetworkNames.BSC: 102,
        NetworkNames.Celo: 125,
        NetworkNames.Core: 153,
        NetworkNames.Fantom: 112,
        NetworkNames.Gnosis: 145,
        NetworkNames.Optimism: 111,
        NetworkNames.Polygon: 109,
        NetworkNames.zkSync_Era: 165,
    },
    'v2': {
        NetworkNames.Arbitrum: 30110,
        NetworkNames.Avalanche: 30103,
        NetworkNames.Base: 30184,
        NetworkNames.BSC: 30102,
        NetworkNames.Celo: 30125,
        NetworkNames.Core: 30153,
        NetworkNames.Fantom: 30112,
        NetworkNames.Gnosis: 30145,
        NetworkNames.Optimism: 30111,
        NetworkNames.Polygon: 30109,
        NetworkNames.zkSync_Era: 30165,
    }
}
