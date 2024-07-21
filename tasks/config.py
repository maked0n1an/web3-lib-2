from libs.async_eth_lib.architecture.network import Network
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.models.others import TokenSymbol


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


def get_stargate_routes() -> dict[Network, dict[str, list[tuple[Network, str]]]]:
    return {
        Networks.Avalanche: {
            TokenSymbol.USDT: [
                (Networks.Arbitrum, TokenSymbol.USDT),
                (Networks.Arbitrum, TokenSymbol.USDC_E),
                (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.BSC,      TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.USDC: [
                (Networks.Arbitrum, TokenSymbol.USDT),
                (Networks.Arbitrum, TokenSymbol.USDC_E),
                (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.BSC,      TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.STG: [
                (Networks.Arbitrum, TokenSymbol.STG),
                (Networks.BSC,      TokenSymbol.STG),
                (Networks.Fantom,   TokenSymbol.STG),
                (Networks.Optimism, TokenSymbol.STG),
                (Networks.Polygon,  TokenSymbol.STG),
            ],
            TokenSymbol.USDV: [
                (Networks.Arbitrum, TokenSymbol.USDV),
                (Networks.BSC,      TokenSymbol.USDV),
                (Networks.Optimism, TokenSymbol.USDV),
                (Networks.Polygon,  TokenSymbol.USDV),
            ],
        },
        Networks.Arbitrum: {
            TokenSymbol.ETH: [
                (Networks.Optimism, TokenSymbol.ETH),
            ],
            TokenSymbol.USDT: [
                (Networks.Avalanche, TokenSymbol.USDC),
                (Networks.Avalanche, TokenSymbol.USDT),
                (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.BSC,      TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.USDC_E: [
                (Networks.Avalanche, TokenSymbol.USDT),
                (Networks.Avalanche, TokenSymbol.USDC_E),
                (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.BSC,      TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.STG: [
                (Networks.Avalanche, TokenSymbol.STG),
                (Networks.BSC,      TokenSymbol.STG),
                (Networks.Fantom,   TokenSymbol.STG),
                (Networks.Optimism, TokenSymbol.STG),
                (Networks.Polygon,  TokenSymbol.STG),
            ],
            TokenSymbol.USDV: [
                (Networks.Arbitrum, TokenSymbol.USDV),
                (Networks.BSC,      TokenSymbol.USDV),
                (Networks.Optimism, TokenSymbol.USDV),
                (Networks.Polygon,  TokenSymbol.USDV),
            ],
        },
        Networks.BSC: {
            TokenSymbol.USDT: [
                (Networks.Arbitrum, TokenSymbol.USDT),
                (Networks.Arbitrum, TokenSymbol.USDC_E),
                (Networks.Arbitrum, TokenSymbol.USDV),
                (Networks.Avalanche, TokenSymbol.USDC),
                (Networks.Avalanche, TokenSymbol.USDT),
                (Networks.Avalanche, TokenSymbol.USDV),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Polygon,  TokenSymbol.USDV),
                (Networks.Optimism, TokenSymbol.USDC_E),
                (Networks.Optimism, TokenSymbol.USDV),
            ],
            TokenSymbol.STG: [
                (Networks.Avalanche, TokenSymbol.STG),
                (Networks.Arbitrum, TokenSymbol.STG),
                # (Networks.Fantom,   TokenSymbol.STG),
                (Networks.Optimism, TokenSymbol.STG),
                (Networks.Polygon,  TokenSymbol.STG),
            ],
            TokenSymbol.USDV: [
                (Networks.Arbitrum, TokenSymbol.USDV),
                (Networks.BSC,      TokenSymbol.USDV),
                (Networks.Optimism, TokenSymbol.USDV),
                (Networks.Polygon,  TokenSymbol.USDV),
            ],
        },
        Networks.Optimism: {
            TokenSymbol.ETH: [
                (Networks.Arbitrum, TokenSymbol.ETH),
            ],
            TokenSymbol.USDC_E: [
                (Networks.Arbitrum, TokenSymbol.USDT),
                (Networks.Arbitrum, TokenSymbol.USDC_E),
                (Networks.Arbitrum, TokenSymbol.USDV),
                (Networks.Avalanche, TokenSymbol.USDC),
                (Networks.Avalanche, TokenSymbol.USDT),
                (Networks.Avalanche, TokenSymbol.USDV),
                (Networks.BSC,      TokenSymbol.USDC_E),
                (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.BSC,      TokenSymbol.USDV),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Polygon,  TokenSymbol.USDV),
            ],
            TokenSymbol.STG: [
                (Networks.Avalanche, TokenSymbol.STG),
                (Networks.Arbitrum, TokenSymbol.STG),
                # (Networks.Fantom, TokenSymbol.STG),
                (Networks.BSC,      TokenSymbol.STG),
                (Networks.Polygon,  TokenSymbol.STG),
            ],
            TokenSymbol.USDV: [
                (Networks.Arbitrum, TokenSymbol.USDV),
                (Networks.Avalanche, TokenSymbol.USDV),
                (Networks.BSC,      TokenSymbol.USDV),
                (Networks.Polygon,  TokenSymbol.USDV),
            ],
        },
        Networks.Polygon: {
            TokenSymbol.USDC_E: [
                (Networks.Arbitrum, TokenSymbol.USDT),
                (Networks.Arbitrum, TokenSymbol.USDC_E),
                (Networks.Avalanche, TokenSymbol.USDC),
                (Networks.Avalanche, TokenSymbol.USDT),
                (Networks.BSC,      TokenSymbol.USDT),
                # (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.USDT: [
                (Networks.Arbitrum, TokenSymbol.USDT),
                (Networks.Arbitrum, TokenSymbol.USDC_E),
                (Networks.Avalanche, TokenSymbol.USDC),
                (Networks.Avalanche, TokenSymbol.USDT),
                (Networks.BSC,      TokenSymbol.USDT),
                # (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.STG: [
                (Networks.Avalanche, TokenSymbol.STG),
                (Networks.Arbitrum, TokenSymbol.STG),
                # (Networks.Fantom,   TokenSymbol.STG),
                (Networks.BSC,      TokenSymbol.STG),
                (Networks.Optimism, TokenSymbol.STG),
            ],
            TokenSymbol.USDV: [
                (Networks.Arbitrum, TokenSymbol.USDV),
                (Networks.Avalanche, TokenSymbol.USDV),
                (Networks.BSC,      TokenSymbol.USDV),
                (Networks.Optimism, TokenSymbol.USDV),
            ]
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
        Networks.ZkSync: {
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
        Networks.ZkSync: {
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
