from src._types.networks import NetworkNames
from src._types.tokens import TokenSymbol
from src.libs.async_eth_lib.utils.helpers import read_json
from src.tasks._common.utils import StandardSettings
from user_data._inputs.settings._global import MODULES_SETTINGS_FILE_PATH


# region Settings
class TestnetBridgeSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)

        self.bridge = StandardSettings(
            settings=settings,
            module_name='testnet_bridge',
            action_name='bridge'
        )
# endregion Settings


class TestnetBridgeData:
    def __init__(self):
        self.contracts = {
            NetworkNames.Arbitrum: {
                TokenSymbol.ETH: '0xfca99f4b5186d4bfbdbd2c542dca2eca4906ba45',
            },
            NetworkNames.Optimism: {
                TokenSymbol.ETH: '0x8352C746839699B1fc631fddc0C3a00d4AC71A17',
            },
        }

def get_testnet_bridge_routes(
) -> dict[NetworkNames, dict[TokenSymbol, list[tuple[NetworkNames, TokenSymbol]]]]:
    return {
        NetworkNames.Arbitrum: {
            TokenSymbol.ETH: [
                (NetworkNames.Sepolia, TokenSymbol.ETH),
            ],
        },
        NetworkNames.Optimism: {
            TokenSymbol.ETH: [
                (NetworkNames.Sepolia, TokenSymbol.ETH),
            ],
        },
        NetworkNames.Sepolia: {
            TokenSymbol.ETH: [
                (NetworkNames.Optimism, TokenSymbol.ETH),
                (NetworkNames.Arbitrum, TokenSymbol.ETH),
            ],
        }
    }

L0_IDS = {
    'v1': {
        NetworkNames.Ethereum: 101,
        NetworkNames.Arbitrum: 110,
        NetworkNames.Optimism: 111,
    },
}