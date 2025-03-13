from src._types.networks import NetworkNamesEnum


PUBLIC_RPCS = {
    # region EVM Mainnets
    NetworkNamesEnum.ETHEREUM: [
        # 'https://eth-mainnet.public.blastapi.io',
        # 'https://ethereum.publicnode.com',
        'https://rpc.ankr.com/eth',
        'https://eth.llamarpc.com',
    ],

    NetworkNamesEnum.ARBITRUM: [
        # 'https://arbitrum-one.public.blastapi.io',
        # 'https://arbitrum-one.publicnode.com',
        'https://arb1.arbitrum.io/rpc',
        # 'https://rpc.ankr.com/arbitrum',
        'https://arbitrum.llamarpc.com'
    ],

    NetworkNamesEnum.ARBITRUM_NOVA: [
        'https://nova.arbitrum.io/rpc/'
    ],

    NetworkNamesEnum.AVALANCHE: [
        'https://rpc.ankr.com/avalanche/'
    ],

    NetworkNamesEnum.BASE: [
        # 'https://base-mainnet.public.blastapi.io',
        # 'https://base.publicnode.com',
        'https://base.llamarpc.com'
    ],

    NetworkNamesEnum.BSC: [
        # 'https://bsc-mainnet.public.blastapi.io',
        # 'https://bsc.publicnode.com',
        # 'https://rpc.ankr.com/bsc',
        'https://bsc-pokt.nodies.app',
    ],

    NetworkNamesEnum.CELO: [
        'https://1rpc.io/celo',
        'https://rpc.ankr.com/celo'
    ],

    NetworkNamesEnum.CORE: [
        'https://1rpc.io/core',
        'https://rpc.ankr.com/core'
    ],

    NetworkNamesEnum.FANTOM: [
        'https://fantom.publicnode.com',
        'https://rpc.ankr.com/fantom',
    ],

    NetworkNamesEnum.GNOSIS: [
        'https://rpc.ankr.com/gnosis'
    ],

    NetworkNamesEnum.HECO: [
        'https://http-mainnet.hecochain.com'
    ],

    NetworkNamesEnum.KAVA: [
        'https://rpc.ankr.com/kava_evm'
    ],

    NetworkNamesEnum.MOONBEAM: [
        'https://rpc.api.moonbeam.network/'
    ],

    NetworkNamesEnum.OP_BNB: [
        'https://opbnb.publicnode.com',
        # 'https://opbnb-mainnet-rpc.bnbchain.org'
    ],

    NetworkNamesEnum.OPTIMISM: [
        # 'https://optimism-mainnet.public.blastapi.io',
        # 'https://optimism.publicnode.com',
        # 'https://mainnet.optimism.io',
        'https://rpc.ankr.com/optimism/'
    ],

    NetworkNamesEnum.POLYGON: [
        # 'https://polygon-mainnet.public.blastapi.io',
        # 'https://polygon-rpc.com',
        'https://rpc.ankr.com/polygon'
    ],
    # endregion EVM Mainnets

    # region EVM Testnets
    NetworkNamesEnum.ETH_GOERLI: [
        'https://rpc.ankr.com/eth_goerli/'
    ],

    NetworkNamesEnum.ETH_SEPOLIA: [
        'https://rpc.sepolia.org',
        # 'https://ethereum-sepolia-rpc.publicnode.com',
        # 'https://1rpc.io/sepolia',
    ],

    NetworkNamesEnum.ETH_HOLESKY: [
        'https://ethereum-holesky-rpc.publicnode.com',
        'https://endpoints.omniatech.io/v1/eth/holesky/public',
        'https://ethereum-holesky.blockpi.network/v1/rpc/public',
    ],
    # endregion EVM Testnets

    # region ZK Mainnets
    NetworkNamesEnum.ZKSYNC_ERA: [
        'https://zksync-era.blockpi.network/v1/rpc/public'
    ],

    NetworkNamesEnum.STARKNET: [
        'https://starknet-mainnet.public.blastapi.io',
    ]
    # endregion ZK Mainnets
}