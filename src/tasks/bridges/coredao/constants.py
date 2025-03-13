from enum import Enum
from typing import cast

from src.libs.async_eth_lib.utils.helpers import read_json
from src._types.networks import NetworkNamesEnum
from src._types.tokens import TokenSymbol
from src.tasks._common.utils import StandardSettings
from user_data._inputs.settings._global import MODULES_SETTINGS_FILE_PATH

# region Settings
class CoreDaoBridgeSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)

        self.bridge = StandardSettings(
            settings=cast(dict, settings),
            module_name='coredao',
            action_name='bridge'
        )
# endregion Settings


class CoreDaoBridgeABIs:
    TO_CORE_BRIDGE_ABI =    ['src', 'data', 'abis', 'coredao', 'to_core_bridge_abi.json']
    FROM_CORE_BRIDGE_ABI =  ['src', 'data', 'abis', 'coredao', 'from_core_bridge_abi.json']


class CoreDaoBridgeData:
    def __init__(self):
        self.contracts = {
            NetworkNamesEnum.ARBITRUM: {
                TokenSymbol.USDT: '0x29d096cD18C0dA7500295f082da73316d704031A',
                TokenSymbol.USDC: '0x29d096cD18C0dA7500295f082da73316d704031A',
            },
            NetworkNamesEnum.AVALANCHE: {
                TokenSymbol.USDT: '0x29d096cD18C0dA7500295f082da73316d704031A',
                TokenSymbol.USDC: '0x29d096cD18C0dA7500295f082da73316d704031A',
            },
            NetworkNamesEnum.BSC: {
                TokenSymbol.USDT: '0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
                TokenSymbol.USDC: '0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
            },
            NetworkNamesEnum.CORE: {
                TokenSymbol.USDT: '0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE',
                TokenSymbol.USDC: '0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE',
            },
            NetworkNamesEnum.OPTIMISM: {
                TokenSymbol.USDT: '0x29d096cD18C0dA7500295f082da73316d704031A',
                TokenSymbol.USDC: '0x29d096cD18C0dA7500295f082da73316d704031A',
            },
            NetworkNamesEnum.POLYGON: {
                TokenSymbol.USDT: '0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
                TokenSymbol.USDC: '0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
            }
        }

def get_coredao_bridge_routes():
    return {
        NetworkNamesEnum.ARBITRUM: {
            TokenSymbol.USDT: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDC)
            ]
        },
        NetworkNamesEnum.AVALANCHE: {
            TokenSymbol.USDT: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDC)
            ]
        },
        NetworkNamesEnum.BSC: {
            TokenSymbol.USDT: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDC)
            ]
        },
        NetworkNamesEnum.OPTIMISM: {
            TokenSymbol.USDT: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDC)
            ]
        },
        NetworkNamesEnum.POLYGON: {
            TokenSymbol.USDT: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNamesEnum.CORE, TokenSymbol.USDC)
            ]
        },
        NetworkNamesEnum.CORE: {
            TokenSymbol.USDT: [
                (NetworkNamesEnum.ARBITRUM,     TokenSymbol.USDT),
                (NetworkNamesEnum.AVALANCHE,    TokenSymbol.USDT),
                (NetworkNamesEnum.BSC,          TokenSymbol.USDT),
                (NetworkNamesEnum.OPTIMISM,     TokenSymbol.USDT),
                (NetworkNamesEnum.POLYGON,      TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (NetworkNamesEnum.ARBITRUM,     TokenSymbol.USDC),
                (NetworkNamesEnum.AVALANCHE,    TokenSymbol.USDC),
                (NetworkNamesEnum.BSC,          TokenSymbol.USDC),
                (NetworkNamesEnum.OPTIMISM,     TokenSymbol.USDC),
                (NetworkNamesEnum.POLYGON,      TokenSymbol.USDC),
            ],
        }
    }


L0_IDS = {
    'v1': {
        NetworkNamesEnum.ETHEREUM: 101,
        NetworkNamesEnum.ARBITRUM: 110,
        NetworkNamesEnum.AVALANCHE: 103,
        NetworkNamesEnum.BASE: 184,
        NetworkNamesEnum.BSC: 102,
        NetworkNamesEnum.CELO: 125,
        NetworkNamesEnum.CORE: 153,
        NetworkNamesEnum.FANTOM: 112,
        NetworkNamesEnum.GNOSIS: 145,
        NetworkNamesEnum.OPTIMISM: 111,
        NetworkNamesEnum.POLYGON: 109,
        NetworkNamesEnum.ZKSYNC_ERA: 165,
    },
    'v2': {
        NetworkNamesEnum.ARBITRUM: 30110,
        NetworkNamesEnum.AVALANCHE: 30103,
        NetworkNamesEnum.BASE: 30184,
        NetworkNamesEnum.BSC: 30102,
        NetworkNamesEnum.CELO: 30125,
        NetworkNamesEnum.CORE: 30153,
        NetworkNamesEnum.FANTOM: 30112,
        NetworkNamesEnum.GNOSIS: 30145,
        NetworkNamesEnum.OPTIMISM: 30111,
        NetworkNamesEnum.POLYGON: 30109,
        NetworkNamesEnum.ZKSYNC_ERA: 30165,
    }
}
