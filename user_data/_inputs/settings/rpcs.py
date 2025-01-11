from _types.networks import NetworkNames


PUBLIC_RPCS = {
    # region EVM Mainnets
    NetworkNames.Ethereum: [
        # 'https://eth-mainnet.public.blastapi.io',
        # 'https://ethereum.publicnode.com',
        'https://rpc.ankr.com/eth',
        'https://eth.llamarpc.com',
    ],

    NetworkNames.Arbitrum: [
        # 'https://arbitrum-one.public.blastapi.io',
        # 'https://arbitrum-one.publicnode.com',
        'https://arb1.arbitrum.io/rpc',
        # 'https://rpc.ankr.com/arbitrum',
        'https://arbitrum.llamarpc.com'
    ],

    NetworkNames.Arbitrum_Nova: [
        'https://nova.arbitrum.io/rpc/'
    ],

    NetworkNames.Avalanche: [
        'https://rpc.ankr.com/avalanche/'
    ],

    NetworkNames.Base: [
        # 'https://base-mainnet.public.blastapi.io',
        # 'https://base.publicnode.com',
        'https://base.llamarpc.com'
    ],

    NetworkNames.BSC: [
        # 'https://bsc-mainnet.public.blastapi.io',
        # 'https://bsc.publicnode.com',
        # 'https://rpc.ankr.com/bsc',
        'https://bsc-pokt.nodies.app',
    ],

    NetworkNames.Celo: [
        'https://1rpc.io/celo',
        'https://rpc.ankr.com/celo'
    ],

    NetworkNames.Core: [
        'https://1rpc.io/core',
        'https://rpc.ankr.com/core'
    ],

    NetworkNames.Fantom: [
        'https://fantom.publicnode.com',
        'https://rpc.ankr.com/fantom',
    ],

    NetworkNames.Gnosis: [
        'https://rpc.ankr.com/gnosis'
    ],

    NetworkNames.Heco: [
        'https://http-mainnet.hecochain.com'
    ],

    NetworkNames.Kava: [
        'https://rpc.ankr.com/kava_evm'
    ],

    NetworkNames.Moonbeam: [
        'https://rpc.api.moonbeam.network/'
    ],

    NetworkNames.opBNB: [
        'https://opbnb.publicnode.com',
        # 'https://opbnb-mainnet-rpc.bnbchain.org'
    ],

    NetworkNames.Optimism: [
        # 'https://optimism-mainnet.public.blastapi.io',
        # 'https://optimism.publicnode.com',
        # 'https://mainnet.optimism.io',
        'https://rpc.ankr.com/optimism/'
    ],

    NetworkNames.Polygon: [
        # 'https://polygon-mainnet.public.blastapi.io',
        # 'https://polygon-rpc.com',
        'https://rpc.ankr.com/polygon'
    ],
    # endregion EVM Mainnets

    # region EVM Testnets
    NetworkNames.Goerli: [
        'https://rpc.ankr.com/eth_goerli/'
    ],

    NetworkNames.Sepolia: [
        'https://rpc.sepolia.org',
        # 'https://ethereum-sepolia-rpc.publicnode.com',
        # 'https://1rpc.io/sepolia',
    ],

    NetworkNames.Holesky: [
        'https://ethereum-holesky-rpc.publicnode.com',
        'https://endpoints.omniatech.io/v1/eth/holesky/public',
        'https://ethereum-holesky.blockpi.network/v1/rpc/public',
    ],
    # endregion EVM Testnets

    # region ZK Mainnets
    NetworkNames.zkSync_Era: [
        'https://zksync-era.blockpi.network/v1/rpc/public'
    ],

    NetworkNames.Starknet: [
        'https://starknet-mainnet.public.blastapi.io',
    ]
    # endregion ZK Mainnets
}