import asyncio
from curl_cffi import requests

from web3 import AsyncHTTPProvider, AsyncWeb3

from src._types.networks import NetworkNamesEnum
from src._types.tokens import TokenSymbol
from src.helpers.get_rpcs import get_all_rpcs
from .api_clients.evm import EvmApiClient
from .api_clients.zk import ZkApiClient
from ..models import exceptions as exceptions



class Network:
    def __init__(
        self,
        name: NetworkNamesEnum,
        explorer: str,
        chain_id: int | None = None,
        coin_symbol: str | TokenSymbol | None = None,
        tx_type: int = 0,
        api: EvmApiClient | ZkApiClient | None = None
    ):
        self.name = name
        self.rpcs = get_all_rpcs(name)
        self.coin_symbol = self._initialize_coin_symbol(coin_symbol)
        self.decimals = 18
        self.tx_type = tx_type
        self.chain_id = self._initialize_chain_id(chain_id)
        self.explorer = explorer
        self.api = api

    def _initialize_chain_id(self, chain_id: int | None) -> int:
        if chain_id is not None:
            return chain_id
        
        try:
            return asyncio.run(AsyncWeb3(AsyncHTTPProvider(self.rpcs[0])).eth.chain_id)
        except Exception as e:
            raise exceptions.WrongChainId(f'Can not get chainID: {e}')

    def _initialize_coin_symbol(self, coin_symbol: str | TokenSymbol | None) -> str:
        if coin_symbol is not None:
            if isinstance(coin_symbol, TokenSymbol):
                return coin_symbol.value
            else:
                return coin_symbol.upper()

        try:
            response = requests.get('https://chainid.network/chains.json').json()
        except Exception as e:
            raise exceptions.WrongCoinSymbol(f'Can not get coin_symbol: {e}')

        for network in response:
            if network['chainId'] == self.chain_id:
                symbol: str = network['nativeCurrency']['symbol']
                return symbol.upper()

        raise exceptions.WrongCoinSymbol(f'Coin symbol not found for chain id [{self.chain_id}]')
