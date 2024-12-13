import requests

from typing import List
from web3 import Web3

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
        rpc: str | List[str],
        explorer: str,
        chain_id: int | None = None,
        coin_symbol: str | None = None,
        decimals: int = 18,
        tx_type: int = 0,
        api: EvmApiClient | ZkApiClient | None = None
    ):
        self.name = name
        self.explorer = explorer
        self.rpc = rpc
        self.chain_id = chain_id
        self.coin_symbol = coin_symbol
        self.decimals = decimals
        self.tx_type = tx_type
        self.api = api
        
        self._initialize_chain_id()
        self._initialize_coin_symbol()
        self._coin_symbol_to_upper()

    def _initialize_chain_id(self):
        if self.chain_id:
            return
        try:
            self.chain_id = Web3(Web3.AsyncHTTPProvider(self.rpc)).eth.chain_id
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
