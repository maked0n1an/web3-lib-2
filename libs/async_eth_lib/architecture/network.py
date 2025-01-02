from curl_cffi import requests

from web3 import Web3

from shared.get_rpcs import get_all_rpcs
from .api_clients.evm import EvmApiClient
from .api_clients.zk import ZkApiClient
from ..models import exceptions as exceptions


# region Definition class
class Network:
    TX_PATH: str = '/tx/'
    CONTRACT_PATH: str = '/contract/'
    ADDRESS_PATH: str = '/address/'
    
    def __init__(
        self,
        name: str,
        explorer: str,
        chain_id: int | None = None,
        coin_symbol: str | None = None,
        tx_type: int = 0,
        api: EvmApiClient | ZkApiClient | None = None
    ):
        self.name = name
        self.rpcs = get_all_rpcs(name)
        self.explorer = explorer
        self.chain_id = chain_id
        self.coin_symbol = coin_symbol
        self.decimals = 18
        self.tx_type = tx_type
        self.api = api
        
        self._initialize_chain_id()
        self._initialize_coin_symbol()
        self._coin_symbol_to_upper()

    def _initialize_chain_id(self):
        if self.chain_id:
            return
        try:
            self.chain_id = Web3(Web3.AsyncHTTPProvider(self.rpcs[0])).eth.chain_id
        except Exception as e:
            raise exceptions.WrongChainId(f'Can not get chainID: {e}')
        
    def _initialize_coin_symbol(self):
        chain_id_url = 'https://chainid.network/chains.json'
        
        if self.coin_symbol:
            return 
        try:
            response = requests.get(chain_id_url).json()
            for network in response:
                if network['chainId'] == self.chain_id:
                    self.coin_symbol = network['nativeCurrency']['symbol']
                    break
        except Exception as e:
            raise exceptions.WrongCoinSymbol(f'Can not get coin_symbol: {e}')
            
    def _coin_symbol_to_upper(self):
        if self.coin_symbol:
            self.coin_symbol = self.coin_symbol.upper()
#endregion Definition class
