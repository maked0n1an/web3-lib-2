from src.libs.async_eth_lib.architecture.network import Network
from src.libs.async_eth_lib.data.networks import Networks
from src.libs.async_eth_lib.models.others import TokenSymbol


def get_coredao_bridge_routes() -> dict[Network, dict[str, list[tuple[Network, str]]]]:
    return {
        Networks.Arbitrum: {
            TokenSymbol.USDT: [
                (Networks.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (Networks.Core, TokenSymbol.USDC)
            ]
        },
        Networks.Avalanche: {
            TokenSymbol.USDT: [
                (Networks.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (Networks.Core, TokenSymbol.USDC)
            ]
        },
        Networks.BSC: {
            TokenSymbol.USDT: [
                (Networks.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (Networks.Core, TokenSymbol.USDC)
            ]
        },
        Networks.Optimism: {
            TokenSymbol.USDT: [
                (Networks.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (Networks.Core, TokenSymbol.USDC)
            ]
        },
        Networks.Polygon: {
            TokenSymbol.USDT: [
                (Networks.Core, TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (Networks.Core, TokenSymbol.USDC)
            ]
        },
        Networks.Core: {
            TokenSymbol.USDT: [
                (Networks.Arbitrum,     TokenSymbol.USDT),
                (Networks.Avalanche,    TokenSymbol.USDT),
                (Networks.BSC,          TokenSymbol.USDT),
                (Networks.Optimism,     TokenSymbol.USDT),
                (Networks.Polygon,      TokenSymbol.USDT),
            ],
            TokenSymbol.USDC: [
                (Networks.Arbitrum,     TokenSymbol.USDC),
                (Networks.Avalanche,    TokenSymbol.USDC),
                (Networks.BSC,          TokenSymbol.USDC),
                (Networks.Optimism,     TokenSymbol.USDC),
                (Networks.Polygon,      TokenSymbol.USDC),
            ],
        }
    }

def get_testnet_bridge_routes() -> dict[Network, dict[str, list[tuple[Network, str]]]]:
    return {
        Networks.Arbitrum: {
            TokenSymbol.ETH: [
                (Networks.Sepolia, TokenSymbol.ETH),
            ],
        },
        Networks.Optimism: {
            TokenSymbol.ETH: [
                (Networks.Sepolia, TokenSymbol.ETH),
            ],
        },
        Networks.Sepolia: {
            TokenSymbol.ETH: [
                (Networks.Optimism, TokenSymbol.ETH),
                (Networks.Arbitrum, TokenSymbol.ETH),
            ],
        }
    }


def get_mute_paths() -> dict[Network, dict[str, list[str]]]:
    return {
        Networks.zkSync_Era: {
            TokenSymbol.ETH: [
                TokenSymbol.USDC,
                TokenSymbol.USDT,
                TokenSymbol.WBTC,
            ],
            TokenSymbol.USDT: [
                TokenSymbol.ETH,
                TokenSymbol.USDC,
                TokenSymbol.WBTC,
            ],
            TokenSymbol.USDC: [
                TokenSymbol.ETH,
                TokenSymbol.USDT,
                TokenSymbol.WBTC,
            ],
            TokenSymbol.WBTC: [
                TokenSymbol.ETH,
                TokenSymbol.USDT,
                TokenSymbol.USDC,
            ]
        }
    }


def get_space_fi_paths() -> dict[Network, dict[str, list[str]]]:
    return {
        Networks.zkSync_Era: {
            TokenSymbol.ETH: [
                TokenSymbol.USDC,
                TokenSymbol.USDT,
                TokenSymbol.WBTC,
            ],
            TokenSymbol.USDC: [
                TokenSymbol.ETH,
                TokenSymbol.WBTC,
            ],
            TokenSymbol.USDT: [
                TokenSymbol.ETH,
            ],
            TokenSymbol.WBTC: [
                TokenSymbol.ETH,
                TokenSymbol.USDC,
            ]
        }
    }
