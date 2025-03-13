from .common import strEnum


class NetworkNamesEnum(strEnum):
    # Mainnets
    ETHEREUM = 'Ethereum'
    ARBITRUM = 'Arbitrum'
    ARBITRUM_NOVA = 'Arbitrum Nova'
    AVALANCHE = 'Avalanche'
    BASE = 'Base'
    BSC = 'BSC'
    CELO = 'Celo'
    CORE = 'Core'
    FANTOM = 'Fantom'
    GNOSIS = 'Gnosis'
    HECO = 'Heco'
    KAVA = 'Kava'
    MANTLE = 'Mantle'
    MOONBEAM = 'Moonbeam'
    OP_BNB = 'opBNB'
    OPTIMISM = 'Optimism'
    POLYGON = 'Polygon'
    STARKNET = 'Starknet'
    ZKSYNC_ERA = 'zkSync Era'

    # Testnets
    ETH_GOERLI = 'Ethereum Goerli'
    ETH_SEPOLIA = 'Ethereum Sepolia'
    ETH_HOLESKY = 'Ethereum Holesky'