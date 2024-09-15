from . import config as config
from ..architecture.api_clients.zk import ZkApiClient
from ..architecture.api_clients.evm import EvmApiClient
from ..architecture.network import Network
from ..models import exceptions as exceptions
from ..models.common import Singleton
from ..models.others import TokenSymbol


class Networks(metaclass=Singleton):
    # region Mainnets
    Ethereum = Network(
        name='Ethereum',
        rpc='https://rpc.ankr.com/eth',
        chain_id=1,
        tx_type=2,
        coin_symbol=TokenSymbol.ETH,
        decimals=18,
        explorer='https://etherscan.io',
        api=EvmApiClient(
            api_key=config.ETHEREUM_API_KEY,
            api_url='https://api.etherscan.io/api',
            docs='https://docs.etherscan.io/'
        ),
    )

    Arbitrum = Network(
        name='Arbitrum',
        rpc=[
            'https://arbitrum.llamarpc.com'
        ],
        chain_id=42161,
        tx_type=2,
        coin_symbol=TokenSymbol.ETH,
        decimals=18,
        explorer='https://arbiscan.io',
        api=EvmApiClient(
            api_key=config.ARBITRUM_API_KEY,
            api_url='https://api.arbiscan.io/api',
            docs='https://docs.arbiscan.io/'
        ),
    )

    Arbitrum_Nova = Network(
        name='Arbitrum_Nova',
        rpc='https://nova.arbitrum.io/rpc/',
        chain_id=42170,
        tx_type=2,
        coin_symbol=TokenSymbol.ETH,
        decimals=18,
        explorer='https://nova.arbiscan.io',
        api=EvmApiClient(
            api_key=config.ARBITRUM_API_KEY,
            api_url='https://api-nova.arbiscan.io/api',
            docs='https://docs.arbiscan.io/v/nova-arbiscan'
        )
    )

    Avalanche = Network(
        name='Avalanche',
        rpc='https://rpc.ankr.com/avalanche/',
        chain_id=43114,
        tx_type=2,
        coin_symbol=TokenSymbol.AVAX,
        decimals=18,
        explorer='https://snowtrace.io',
        api=EvmApiClient(
            api_key=config.AVALANCHE_API_KEY,
            api_url='https://api.snowtrace.io/api',
            docs='https://docs.snowtrace.io/'
        )
    )

    Base = Network(
        name='Base',
        rpc='https://base.llamarpc.com',
        chain_id=8453,
        tx_type=0,
        coin_symbol=TokenSymbol.ETH,
        decimals=18,
        explorer='https://basescan.org/',
    )

    BSC = Network(
        name='BSC',
        rpc='https://rpc.ankr.com/bsc/',
        chain_id=56,
        tx_type=0,
        coin_symbol=TokenSymbol.BNB,
        decimals=18,
        explorer='https://bscscan.com',
        api=EvmApiClient(
            api_key=config.BSC_API_KEY,
            api_url='https://api.bscscan.com/api',
            docs='https://docs.bscscan.com/'
        ),
    )

    Celo = Network(
        name='Celo',
        rpc='https://1rpc.io/celo',
        chain_id=42220,
        tx_type=0,
        coin_symbol=TokenSymbol.CELO,
        decimals=18,
        explorer='https://celoscan.io',
        api=EvmApiClient(
            api_key=config.CELO_API_KEY,
            api_url='https://api.celoscan.io/api',
            docs='https://celoscan.io/apis/'
        )
    )

    Core = Network(
        name='Core',
        rpc='https://1rpc.io/core',
        chain_id=1116,
        tx_type=0,
        coin_symbol=TokenSymbol.CORE,
        decimals=18,
        explorer='https://scan.coredao.org',
    )

    Fantom = Network(
        name='Fantom',
        rpc='https://fantom.publicnode.com',
        chain_id=250,
        tx_type=0,
        coin_symbol=TokenSymbol.FTM,
        decimals=18,
        explorer='https://ftmscan.com',
        api=EvmApiClient(
            api_key=config.FANTOM_API_KEY,
            api_url='https://api.ftmscan.com/api',
            docs='https://docs.ftmscan.com/'
        )
    )

    Gnosis = Network(
        name='Gnosis',
        rpc='https://rpc.ankr.com/gnosis',
        chain_id=100,
        tx_type=2,
        coin_symbol=TokenSymbol.XDAI,
        decimals=18,
        explorer='https://gnosisscan.io',
        api=EvmApiClient(
            api_key=config.GNOSIS_API_KEY,
            api_url='https://api.gnosisscan.io/api',
            docs='https://docs.gnosisscan.io/'
        )
    )

    Heco = Network(
        name='Heco',
        rpc='https://http-mainnet.hecochain.com',
        chain_id=128,
        tx_type=2,
        coin_symbol=TokenSymbol.HECO,
        decimals=18,
        explorer='https://www.hecoinfo.com/en-us',
        api=EvmApiClient(
            api_key=config.HECO_API_KEY,
            api_url='https://api.hecoinfo.com/api',
            docs='https://hecoinfo.com/apis'
        )
    )

    Kava = Network(
        name='Kava',
        rpc="https://rpc.ankr.com/kava_evm",
        chain_id=2222,
        tx_type=2,
        coin_symbol=TokenSymbol.KAVA,
        decimals=18,
        explorer="https://kavascan.com"
    )

    Moonbeam = Network(
        name='Moonbeam',
        rpc='https://rpc.api.moonbeam.network/',
        chain_id=1284,
        tx_type=2,
        coin_symbol=TokenSymbol.GLMR,
        decimals=18,
        explorer='https://moonscan.io',
        api=EvmApiClient(
            api_key=config.MOONBEAM_API_KEY,
            api_url='https://api-moonbeam.moonscan.io/api',
            docs='https://moonscan.io/apis/'
        )
    )

    opBNB = Network(
        name="opBNB",
        rpc=[
            "https://opbnb.publicnode.com"
        ],
        chain_id=204,
        tx_type=0,
        coin_symbol=TokenSymbol.BNB,
        decimals=18,
        explorer="https://mainnet.opbnbscan.com",
        api=EvmApiClient(
            api_key=config.OPBNB_API_KEY,
            api_url='https://opbnb-mainnet.nodereal.io/v1/',
            docs='https://docs.nodereal.io/reference/opbnb-enhanced-api'
        )
    )

    Optimism = Network(
        name='Optimism',
        rpc='https://rpc.ankr.com/optimism/',
        chain_id=10,
        tx_type=2,
        coin_symbol=TokenSymbol.ETH,
        decimals=18,
        explorer='https://optimistic.etherscan.io',
        api=EvmApiClient(
            api_key=config.OPTIMISM_API_KEY,
            api_url='https://api-optimistic.etherscan.io/api',
            docs='https://docs.optimism.etherscan.io/api-endpoints'
        )
    )

    Polygon = Network(
        name='Polygon',
        rpc='https://rpc.ankr.com/polygon/',
        chain_id=137,
        tx_type=2,
        coin_symbol=TokenSymbol.MATIC,
        decimals=18,
        explorer='https://polygonscan.com',
        api=EvmApiClient(
            api_key=config.POLYGON_API_KEY,
            api_url='https://api.polygonscan.com/api',
            docs='https://docs.polygonscan.com/'
        ),
    )

    zkSync_Era = Network(
        name='zkSync_Era',
        rpc='https://multi-convincing-dust.zksync-mainnet.quiknode.pro/c94ba40682080821bbc8b4dd7ba7360329948422/',
        chain_id=324,
        tx_type=2,
        coin_symbol=TokenSymbol.ETH,
        decimals=18,
        explorer='https://explorer.zksync.io',
        api=ZkApiClient(
            api_url='https://www.oklink.com',
            api_key=config.OKLINK_API_KEY
        )
    )

    # region Testnets
    Goerli = Network(
        name='Goerli',
        rpc='https://rpc.ankr.com/eth_goerli/',
        chain_id=5,
        tx_type=2,
        coin_symbol=TokenSymbol.ETH,
        decimals=18,
        explorer='https://goerli.etherscan.io',
        api=EvmApiClient(
            api_key=config.GOERLI_API_KEY,
            api_url='https://api-goerli.etherscan.io/api',
            docs='https://docs.etherscan.io/v/goerli-etherscan/'
        )
    )

    Sepolia = Network(
        name='Sepolia',
        rpc='https://rpc.sepolia.org',
        chain_id=11155111,
        tx_type=2,
        coin_symbol=TokenSymbol.ETH,
        decimals=18,
        explorer='https://sepolia.etherscan.io',
        api=EvmApiClient(
            api_key=config.SEPOLIA_API_KEY,
            api_url='https://api-sepolia.etherscan.io/api',
            docs='https://docs.etherscan.io/v/sepolia-etherscan/'
        )
    )

    @classmethod
    def get_network(
        cls,
        network_name: str
    ) -> Network:
        if not hasattr(cls, network_name):
            raise exceptions.NetworkNotAdded(
                f"The network has not been added to \"{__class__.__name__}\" class"
            )

        return getattr(cls, network_name)
