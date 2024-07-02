import requests

from typing import List
from web3 import Web3

import libs.async_eth_lib.models.exceptions as exceptions


# region Definition class
class Network:
    TX_PATH: str = '/tx/'
    CONTRACT_PATH: str = '/contract/'
    ADDRESS_PATH: str = '/address/'
    
    def __init__(
        self,
        name: str,
        rpc: str | List[str],
        chain_id: int | None = None,
        tx_type: int = 0,
        coin_symbol: str | None = None,
        decimals: int | None = None,
        explorer: str | None = None,
    ) -> None:
        self.name: str = name.lower()
        self.rpc: str | List[str] = rpc
        self.chain_id: int | None = chain_id
        self.tx_type: int = tx_type
        self.coin_symbol: str | None = coin_symbol
        self.decimals: int | None = decimals
        self.explorer: str | None = explorer
        
        self._initialize_chain_id()
        self._initialize_coin_symbol_and_decimals()
        self._coin_symbol_to_upper()

    def _initialize_chain_id(self):
        if self.chain_id:
            return
        try:
            self.chain_id = Web3(Web3.AsyncHTTPProvider(self.rpc)).eth.chain_id
        except Exception as e:
            raise exceptions.WrongChainId(f'Can not get chainID: {e}')
        
    def _initialize_coin_symbol_and_decimals(self):
        chain_id_url = 'https://chainid.network/chains.json'
        
        if self.coin_symbol and self.decimals:
            return 
        try:
            response = requests.get(chain_id_url).json()
            for network in response:
                if network['chainId'] == self.chain_id:
                    self.coin_symbol = network['nativeCurrency']['symbol']
                    self.decimals = network['nativeCurrency']['decimals']
                    break
        except Exception as e:
            raise exceptions.WrongCoinSymbol(f'Can not get coin_symbol: {e}')
            
    def _coin_symbol_to_upper(self):
        if self.coin_symbol:
            self.coin_symbol = self.coin_symbol.upper()
#endregion Definition class
