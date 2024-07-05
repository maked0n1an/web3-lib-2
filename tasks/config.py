from libs.async_eth_lib.architecture.network import Network
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.models.others import TokenSymbol


class Config:
    STARGATE_ROUTES_FOR_BRIDGE: dict[Network, dict[str, list[tuple[Network, str]]]] = {
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
                (Networks.Avalanche,TokenSymbol.USDC),
                (Networks.Avalanche,TokenSymbol.USDT),
                (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.BSC,      TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.USDC_E: [
                (Networks.Avalanche,TokenSymbol.USDT),
                (Networks.Avalanche,TokenSymbol.USDC_E),
                (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.BSC,      TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.STG: [
                (Networks.Avalanche,TokenSymbol.STG),
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
                (Networks.Avalanche,TokenSymbol.USDC),
                (Networks.Avalanche,TokenSymbol.USDT),
                (Networks.Avalanche,TokenSymbol.USDV),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Polygon,  TokenSymbol.USDV),
                (Networks.Optimism, TokenSymbol.USDC_E),
                (Networks.Optimism, TokenSymbol.USDV),
            ],
            TokenSymbol.STG: [
                (Networks.Avalanche,TokenSymbol.STG),
                (Networks.Arbitrum, TokenSymbol.STG),
                ## (Networks.Fantom,   TokenSymbol.STG),
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
                (Networks.Avalanche,TokenSymbol.USDC),
                (Networks.Avalanche,TokenSymbol.USDT),
                (Networks.Avalanche,TokenSymbol.USDV),
                (Networks.BSC,      TokenSymbol.USDC_E),
                (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.BSC,      TokenSymbol.USDV),
                (Networks.Polygon,  TokenSymbol.USDT),
                (Networks.Polygon,  TokenSymbol.USDC_E),
                (Networks.Polygon,  TokenSymbol.USDV),
            ],
            TokenSymbol.STG: [
                (Networks.Avalanche,TokenSymbol.STG),
                (Networks.Arbitrum, TokenSymbol.STG),
                ## (Networks.Fantom, TokenSymbol.STG),
                (Networks.BSC,      TokenSymbol.STG),
                (Networks.Polygon,  TokenSymbol.STG),
            ],
            TokenSymbol.USDV: [
                (Networks.Arbitrum, TokenSymbol.USDV),
                (Networks.Avalanche,TokenSymbol.USDV),
                (Networks.BSC,      TokenSymbol.USDV),
                (Networks.Polygon,  TokenSymbol.USDV),
            ],
        },
        Networks.Polygon: {
            TokenSymbol.USDC_E: [
                (Networks.Arbitrum, TokenSymbol.USDT),
                (Networks.Arbitrum, TokenSymbol.USDC_E),
                (Networks.Avalanche,TokenSymbol.USDC),
                (Networks.Avalanche,TokenSymbol.USDT),
                (Networks.BSC,      TokenSymbol.USDT),
                ## (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.USDT: [
                (Networks.Arbitrum, TokenSymbol.USDT),
                (Networks.Arbitrum, TokenSymbol.USDC_E),
                (Networks.Avalanche,TokenSymbol.USDC),
                (Networks.Avalanche,TokenSymbol.USDT),
                (Networks.BSC,      TokenSymbol.USDT),
                ## (Networks.BSC,      TokenSymbol.BUSD),
                (Networks.Optimism, TokenSymbol.USDC_E),
            ],
            TokenSymbol.STG: [
                (Networks.Avalanche,TokenSymbol.STG),
                (Networks.Arbitrum, TokenSymbol.STG),
                ## (Networks.Fantom,   TokenSymbol.STG),
                (Networks.BSC,      TokenSymbol.STG),
                (Networks.Optimism, TokenSymbol.STG),
            ],
            TokenSymbol.USDV: [
                (Networks.Arbitrum, TokenSymbol.USDV),
                (Networks.Avalanche, TokenSymbol.USDV),
                (Networks.BSC,      TokenSymbol.USDV),
                (Networks.Optimism, TokenSymbol.USDV),
            ],
        },
    },
    MUTE_PATHS: dict[Network, dict[str, list[str]]] = {
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
            ],
        }
    },
    SPACE_FI_PATHS: dict[Network, dict[str, list[str]]] = {
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
            ],
        }
    }