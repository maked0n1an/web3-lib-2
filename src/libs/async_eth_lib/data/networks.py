from _types.networks import NetworkNames
from ..architecture.api_clients.zk import ZkApiClient
from ..architecture.api_clients.evm import EvmApiClient
from ..architecture.network import Network
from ..models import exceptions as exceptions
from ..models.common import Singleton
from ..models.others import TokenSymbol


class Networks(metaclass=Singleton):
    # region Mainnets
    Ethereum = Network(
        name=NetworkNames.Ethereum,
        explorer='https://etherscan.io',
        chain_id=1,
        coin_symbol=TokenSymbol.ETH,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.ETHEREUM_API_KEY,
        #     api_url='https://api.etherscan.io/api',
        #     docs='https://docs.etherscan.io/'
        # ),
    )

    Arbitrum = Network(
        name=NetworkNames.Arbitrum,
        explorer='https://arbiscan.io',
        chain_id=42161,
        coin_symbol=TokenSymbol.ETH,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.ARBITRUM_API_KEY,
        #     api_url='https://api.arbiscan.io/api',
        #     docs='https://docs.arbiscan.io/'
        # ),
    )

    Arbitrum_Nova = Network(
        name=NetworkNames.Arbitrum_Nova,
        explorer='https://nova.arbiscan.io',
        chain_id=42170,
        coin_symbol=TokenSymbol.ETH,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.ARBITRUM_API_KEY,
        #     api_url='https://api-nova.arbiscan.io/api',
        #     docs='https://docs.arbiscan.io/v/nova-arbiscan'
        # )
    )

    Avalanche = Network(
        name=NetworkNames.Avalanche,
        explorer='https://snowtrace.io',
        chain_id=43114,
        coin_symbol=TokenSymbol.AVAX,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.AVALANCHE_API_KEY,
        #     api_url='https://api.snowtrace.io/api',
        #     docs='https://docs.snowtrace.io/'
        # )
    )

    Base = Network(
        name=NetworkNames.Base,
        explorer='https://basescan.org/',
        chain_id=8453,
        coin_symbol=TokenSymbol.ETH,
        tx_type=0,
    )

    BSC = Network(
        name=NetworkNames.BSC,
        explorer='https://bscscan.com',
        chain_id=56,
        coin_symbol=TokenSymbol.BNB,
        tx_type=0,
        # api=EvmApiClient(
        #     api_key=config.BSC_API_KEY,
        #     api_url='https://api.bscscan.com/api',
        #     docs='https://docs.bscscan.com/'
        # ),
    )

    Celo = Network(
        name=NetworkNames.Celo,
        explorer='https://celoscan.io',
        chain_id=42220,
        coin_symbol=TokenSymbol.CELO,
        tx_type=0,
        # api=EvmApiClient(
        #     api_key=config.CELO_API_KEY,
        #     api_url='https://api.celoscan.io/api',
        #     docs='https://celoscan.io/apis/'
        # )
    )

    Core = Network(
        name=NetworkNames.Core,
        explorer='https://scan.coredao.org',
        chain_id=1116,
        coin_symbol=TokenSymbol.CORE,
        tx_type=0,
    )

    Fantom = Network(
        name=NetworkNames.Fantom,
        explorer='https://ftmscan.com',
        chain_id=250,
        coin_symbol=TokenSymbol.FTM,
        tx_type=0,
        # api=EvmApiClient(
        #     api_key=config.FANTOM_API_KEY,
        #     api_url='https://api.ftmscan.com/api',
        #     docs='https://docs.ftmscan.com/'
        # )
    )

    Gnosis = Network(
        name=NetworkNames.Gnosis,
        explorer='https://gnosisscan.io',
        chain_id=100,
        coin_symbol=TokenSymbol.XDAI,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.GNOSIS_API_KEY,
        #     api_url='https://api.gnosisscan.io/api',
        #     docs='https://docs.gnosisscan.io/'
        # )
    )

    Heco = Network(
        name=NetworkNames.Heco,
        explorer='https://www.hecoinfo.com/en-us',
        chain_id=128,
        coin_symbol=TokenSymbol.HECO,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.HECO_API_KEY,
        #     api_url='https://api.hecoinfo.com/api',
        #     docs='https://hecoinfo.com/apis'
        # )
    )

    Kava = Network(
        name=NetworkNames.Kava,
        explorer="https://kavascan.com",
        chain_id=2222,
        coin_symbol=TokenSymbol.KAVA,
        tx_type=2,
    )

    Moonbeam = Network(
        name=NetworkNames.Moonbeam,
        explorer='https://moonscan.io',
        chain_id=1284,
        coin_symbol=TokenSymbol.GLMR,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.MOONBEAM_API_KEY,
        #     api_url='https://api-moonbeam.moonscan.io/api',
        #     docs='https://moonscan.io/apis/'
        # )
    )

    opBNB = Network(
        name=NetworkNames.opBNB,
        explorer="https://mainnet.opbnbscan.com",
        chain_id=204,
        coin_symbol=TokenSymbol.BNB,
        tx_type=0,
        # api=EvmApiClient(
        #     api_key=config.OPBNB_API_KEY,
        #     api_url='https://opbnb-mainnet.nodereal.io/v1/',
        #     docs='https://docs.nodereal.io/reference/opbnb-enhanced-api'
        # )
    )

    Optimism = Network(
        name=NetworkNames.Optimism,
        explorer='https://optimistic.etherscan.io',
        chain_id=10,
        coin_symbol=TokenSymbol.ETH,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.OPTIMISM_API_KEY,
        #     api_url='https://api-optimistic.etherscan.io/api',
        #     docs='https://docs.optimism.etherscan.io/api-endpoints'
        # )
    )

    Polygon = Network(
        name=NetworkNames.Polygon,
        explorer='https://polygonscan.com',
        chain_id=137,
        coin_symbol=TokenSymbol.POL,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.POLYGON_API_KEY,
        #     api_url='https://api.polygonscan.com/api',
        #     docs='https://docs.polygonscan.com/'
        # )
    )

    zkSync_Era = Network(
        name=NetworkNames.zkSync_Era,
        explorer='https://explorer.zksync.io',
        chain_id=324,
        coin_symbol=TokenSymbol.ETH,
        tx_type=2,
        # api=ZkApiClient(
        #     api_url='https://www.oklink.com',
        #     api_key=config.OKLINK_API_KEY
        # )
    )

    # region Testnets
    Goerli = Network(
        name=NetworkNames.Goerli,
        explorer='https://goerli.etherscan.io',
        chain_id=5,
        coin_symbol=TokenSymbol.ETH,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.GOERLI_API_KEY,
        #     api_url='https://api-goerli.etherscan.io/api',
        #     docs='https://docs.etherscan.io/v/goerli-etherscan/'
        # )
    )

    Sepolia = Network(
        name=NetworkNames.Sepolia,
        explorer='https://sepolia.etherscan.io',
        chain_id=11155111,
        coin_symbol=TokenSymbol.ETH,
        tx_type=2,
        # api=EvmApiClient(
        #     api_key=config.SEPOLIA_API_KEY,
        #     api_url='https://api-sepolia.etherscan.io/api',
        #     docs='https://docs.etherscan.io/v/sepolia-etherscan/'
        # )
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
