from src.libs.async_eth_lib.architecture.network import Network
from src.libs.async_eth_lib.data.networks import Networks
from src.libs.async_eth_lib.models.others import TokenSymbol

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
