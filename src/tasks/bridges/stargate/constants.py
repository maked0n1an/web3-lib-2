from enum import Enum

from src.libs.async_eth_lib.utils.helpers import read_json
from src._types.networks import NetworkNames
from src._types.tokens import TokenSymbol
from src.tasks._common.utils import StandardSettings


# region Settings
class StargateSettings():
    def __init__(self):
        settings = read_json(path=['user_data', '_inputs', 'json', 'settings.json'])

        self.bridge_type: dict[str, bool] = settings['stargate']['bridge_type']
        self.bridge = StandardSettings(
            settings=settings,
            module_name='stargate',
            action_name='bridge'
        )

        self.slippage_and_gas: float = settings['stargate']['slippage_and_gas']
# endregion Settings


class StargateABIs:
    ROUTER_ETH_V1_ABI = ('src', 'data', 'abis', 'stargate', 'router_eth_abi.json')
    ROUTER_V1_ABI =     ('src', 'data', 'abis', 'stargate', 'router_abi.json')
    MESSAGING_V1_ABI =  ('src', 'data', 'abis', 'stargate', 'msg_abi.json')
    STG_ABI =           ('src', 'data', 'abis', 'stargate', 'stg_abi.json')
    BRIDGE_RECOLOR =    ('src', 'data', 'abis', 'stargate', 'bridge_recolor.json')

    V2_ABI =            ('src', 'data', 'abis', 'stargate', 'router_abi_v2.json')


class BridgeType(str, Enum):
    Fast: str = '0x'  # bridge by 'taxi' type
    Economy: str = '0x01'  # bridge by 'bus' type


class StargateData:
    def __init__(self):
        self.v1 = {
            NetworkNames.Arbitrum: {
                TokenSymbol.ETH: '0xbf22f0f184bCcbeA268dF387a49fF5238dD23E40',
                TokenSymbol.USDT: '0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
                TokenSymbol.USDC_E: '0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
                TokenSymbol.STG: '0x6694340fc020c5e6b96567843da2df01b2ce1eb6',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
            NetworkNames.Avalanche: {
                TokenSymbol.USDT: '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                TokenSymbol.USDC: '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                TokenSymbol.STG: '0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
            NetworkNames.BSC: {
                TokenSymbol.USDT: '0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
                TokenSymbol.BUSD: '0xB16f5A073d72cB0CF13824d65aA212a0e5c17D63',
                # TokenSymbol.USDV + '-other': '0x5B1d0467BED2e8Bd67c16cE8bCB22a195ae76870',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
            NetworkNames.Fantom: {
                TokenSymbol.USDC: '0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6',
            },
            NetworkNames.Optimism: {
                TokenSymbol.ETH: '0xB49c4e680174E331CB0A7fF3Ab58afC9738d5F8b',
                TokenSymbol.USDC_E: '0xb0d502e938ed5f4df2e681fe6e419ff29631d62b',
                TokenSymbol.STG: '0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f97',
                # TokenSymbol.USDV + '-other': '0x31691Fd2Cf50c777943b213836C342327f0DAB9b',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
            NetworkNames.Polygon: {
                TokenSymbol.USDT: '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                TokenSymbol.USDC_E: '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                TokenSymbol.STG: '0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
        }
        self.v2 = {
            NetworkNames.Arbitrum: {
                TokenSymbol.ETH: '0xA45B5130f36CDcA45667738e2a258AB09f4A5f7F',
                TokenSymbol.USDT: '0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0',
                TokenSymbol.USDT + '-other': '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614',
                TokenSymbol.USDC: '0xe8CDF27AcD73a434D661C84887215F7598e7d0d3',
                TokenSymbol.USDC_E: '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614',
                TokenSymbol.USDC_E + '-other': '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614',
                TokenSymbol.STG: '0x6694340fc020c5E6B96567843da2df01b2CE1eb6',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
            NetworkNames.Avalanche: {
                TokenSymbol.USDT: '0x12dC9256Acc9895B076f6638D628382881e62CeE',
                TokenSymbol.USDT + '-other': '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                TokenSymbol.USDC: '0x5634c4a5FEd09819E3c46D86A965Dd9447d86e47',
                TokenSymbol.USDC + '-other': '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
                TokenSymbol.STG: '0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
            NetworkNames.Base: {
                TokenSymbol.ETH: '0x50B6EbC2103BFEc165949CC946d739d5650d7ae4',
                TokenSymbol.STG: '0xE3B53AF74a4BF62Ae5511055290838050bf764Df',
            },
            NetworkNames.BSC: {
                TokenSymbol.USDT: '0x138EB30f73BC423c6455C53df6D89CB01d9eBc63',
                TokenSymbol.USDT + '-other': '0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
                TokenSymbol.STG: '0xB0D502E938ed5f4df2E681fE6E419ff29631d62b',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
            NetworkNames.Optimism: {
                TokenSymbol.ETH: '0xe8CDF27AcD73a434D661C84887215F7598e7d0d3',
                TokenSymbol.USDT: '0x19cFCE47eD54a88614648DC3f19A5980097007dD',
                TokenSymbol.USDC: '0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0',
                TokenSymbol.STG: '0x6694340fc020c5E6B96567843da2df01b2CE1eb6',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
            NetworkNames.Polygon: {
                TokenSymbol.USDT: '0xd47b03ee6d86Cf251ee7860FB2ACf9f91B9fD4d7',
                TokenSymbol.USDC: '0x9Aa02D4Fae7F58b8E8f34c66E756cC734DAc7fe4',
                TokenSymbol.STG: '0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
                TokenSymbol.USDV: '0x323665443CEf804A3b5206103304BD4872EA4253',
            },
        }

    def get_contract_address(
        self,
        network: NetworkNames,
        from_token: TokenSymbol,
        to_token: TokenSymbol,
        version: str = 'v1'
    ) -> str:
        if version == 'v1':
            data = self.v1
        elif version == 'v2':
            data = self.v2

        if from_token != to_token:
            if to_token == TokenSymbol.USDV:
                return data[network][TokenSymbol.USDV + '-other']
            return data[network][from_token + '-other']
        else:
            return data[network][from_token]


def get_stargate_routes(
) -> dict[NetworkNames, dict[TokenSymbol, list[tuple[NetworkNames, TokenSymbol, BridgeType]]]]:
    return {
        NetworkNames.Avalanche: {
            TokenSymbol.USDT: [
                (NetworkNames.Arbitrum, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Core,     TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Polygon,  TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Optimism, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Arbitrum, TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Fantom,   TokenSymbol.USDC, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDC_E, BridgeType.Fast),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Arbitrum, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Polygon,  TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Arbitrum, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Base,     TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Core,     TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Optimism, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Polygon,  TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Arbitrum, TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDC_E, BridgeType.Fast),
            ],
            TokenSymbol.STG: [
                (NetworkNames.Arbitrum, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.BSC,      TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Fantom,   TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.STG, BridgeType.Fast),
            ],
            TokenSymbol.USDV: [
                (NetworkNames.Arbitrum, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.BSC,      TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDV, BridgeType.Fast),
            ],
        },
        NetworkNames.Arbitrum: {
            TokenSymbol.ETH: [
                (NetworkNames.Base, TokenSymbol.ETH, BridgeType.Economy),
                (NetworkNames.Optimism, TokenSymbol.ETH, BridgeType.Economy),
            ],
            TokenSymbol.USDT: [
                (NetworkNames.Avalanche, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Core,     TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Optimism, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Polygon,  TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Fantom,   TokenSymbol.USDC, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDC_E, BridgeType.Fast),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Avalanche, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Polygon,  TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Fantom,   TokenSymbol.USDC, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDC_E, BridgeType.Fast),
            ],
            TokenSymbol.USDC_E: [
                (NetworkNames.Avalanche, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Polygon,  TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Fantom,   TokenSymbol.USDC, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDC_E, BridgeType.Fast),
            ],
            TokenSymbol.STG: [
                (NetworkNames.Avalanche, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.BSC,      TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Fantom,   TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.STG, BridgeType.Fast),
            ],
            TokenSymbol.USDV: [
                (NetworkNames.Avalanche, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.BSC,      TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDV, BridgeType.Fast),
            ],
        },
        NetworkNames.Base: {
            TokenSymbol.ETH: [
                (NetworkNames.Arbitrum, TokenSymbol.ETH, BridgeType.Economy),
                (NetworkNames.Optimism, TokenSymbol.ETH, BridgeType.Economy),
            ],
            TokenSymbol.STG: [
                (NetworkNames.Avalanche, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.BSC,      TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Fantom,   TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.STG, BridgeType.Fast),
            ],
        },
        NetworkNames.BSC: {
            TokenSymbol.USDT: [
                (NetworkNames.Arbitrum, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Core,     TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Polygon,  TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Optimism, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Fantom,   TokenSymbol.USDC, BridgeType.Fast),
                (NetworkNames.Arbitrum, TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDC_E, BridgeType.Fast),
            ],
            TokenSymbol.STG: [
                (NetworkNames.Avalanche, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Arbitrum, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Base,     TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Fantom,   TokenSymbol.STG, BridgeType.Fast),
            ],
            TokenSymbol.USDV: [
                (NetworkNames.Arbitrum, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Avalanche, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDV, BridgeType.Fast),
            ],
        },
        NetworkNames.Optimism: {
            TokenSymbol.ETH: [
                (NetworkNames.Base, TokenSymbol.ETH, BridgeType.Economy),
                (NetworkNames.Optimism, TokenSymbol.ETH, BridgeType.Economy),
            ],
            TokenSymbol.USDT: [
                (NetworkNames.Arbitrum, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Core,     TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Polygon,  TokenSymbol.USDT, BridgeType.Economy),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Arbitrum, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Base,     TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Polygon,  TokenSymbol.USDC, BridgeType.Economy),
            ],
            TokenSymbol.STG: [
                (NetworkNames.Avalanche, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Arbitrum, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.BSC,      TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Base,     TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Fantom,   TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.STG, BridgeType.Fast),
            ],
            TokenSymbol.USDV: [
                (NetworkNames.Arbitrum, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Avalanche, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.BSC,      TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Polygon,  TokenSymbol.USDV, BridgeType.Fast),
            ],
        },
        NetworkNames.Polygon: {
            TokenSymbol.USDT: [
                (NetworkNames.Arbitrum, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Core,     TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Optimism, TokenSymbol.USDT, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Fantom,   TokenSymbol.USDC, BridgeType.Fast),
                (NetworkNames.Arbitrum, TokenSymbol.USDC_E, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDC_E, BridgeType.Fast),
            ],
            TokenSymbol.USDC: [
                (NetworkNames.Arbitrum, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Avalanche, TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Base,     TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.BSC,      TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Core,     TokenSymbol.USDC, BridgeType.Economy),
                (NetworkNames.Optimism, TokenSymbol.USDC, BridgeType.Economy),
            ],
            TokenSymbol.STG: [
                (NetworkNames.Avalanche, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Arbitrum, TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.BSC,      TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Base,     TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Fantom,   TokenSymbol.STG, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.STG, BridgeType.Fast),
            ],
            TokenSymbol.USDV: [
                (NetworkNames.Arbitrum, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Avalanche, TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.BSC,      TokenSymbol.USDV, BridgeType.Fast),
                (NetworkNames.Optimism, TokenSymbol.USDV, BridgeType.Fast),
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


POOL_IDS = {
    NetworkNames.Ethereum: {
        TokenSymbol.USDC: 1,
        TokenSymbol.USDT: 2,
        TokenSymbol.DAI: 3,
        TokenSymbol.ETH: 13,
    },
    NetworkNames.Arbitrum: {
        TokenSymbol.USDC: 1,
        TokenSymbol.USDT: 2,
        TokenSymbol.ETH: 13,
    },
    NetworkNames.Avalanche: {
        TokenSymbol.USDC: 1,
        TokenSymbol.USDT: 2,
    },
    NetworkNames.Base: {
        TokenSymbol.USDC: 1,
        TokenSymbol.ETH: 13,
    },
    NetworkNames.BSC: {
        TokenSymbol.USDT: 2,
        TokenSymbol.BUSD: 5,
    },
    NetworkNames.Fantom: {
        TokenSymbol.USDC: 21,
    },
    NetworkNames.Optimism: {
        TokenSymbol.USDC_E: 1,
        TokenSymbol.DAI: 3,
        TokenSymbol.ETH: 13,
    },
    NetworkNames.Polygon: {
        TokenSymbol.USDC: 1,
        TokenSymbol.USDT: 2,
        TokenSymbol.DAI: 3,
    }
}
