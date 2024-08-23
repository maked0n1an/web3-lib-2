from typing import Any

from fake_useragent import UserAgent

import libs.async_eth_lib.models.exceptions as exceptions
from libs.async_eth_lib.architecture.api_clients.utils import api_key_required
from libs.async_eth_lib.models.explorer import Sort, Tag
from libs.async_eth_lib.utils.helpers import make_async_request

# region MainClass
class EvmApiClient:
    """
    Class with functions related to Blockscan API.
    """

    def __init__(self, api_url: str, api_key: str, docs: str = ''):
        """
        Initialize the class.

        Args:
            api_key (str): an API key.
            api_url (str): an API entrypoint URL.

        """
        self.api_key = api_key
        self.api_url = api_url
        self.docs = docs
        self.headers = self._init_headers()

        self.account = Account(api_key, api_url, self.headers)
        self.contract = Contract(api_key, api_url, self.headers)
        self.transaction = Transaction(api_key, api_url, self.headers)
        # self.block = Block(self.key, self.url, self.headers)
        # self.logs = Logs(self.key, self.url, self.headers)
        # self.token = Token(self.key, self.url, self.headers)
        # self.gastracker = Gastracker(self.key, self.url, self.headers)
        # self.stats = Stats(self.key, self.url, self.headers)

    def _init_headers(self):
        return {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'User-Agent': UserAgent().random
        }
# endregion MainClass


# region Components
class Module:
    """
    Class with functions related to some API module.
    """
    MODULE_NAME: str = ''

    def __init__(
        self,
        api_key: str,
        api_url: str,
        headers: dict[str, Any]
    ) -> None:
        """
        Initialize the class.

        Args:
            key (str): an API key.
            url (str): an API entrypoint URL.
            headers (dict[str, Any]): a headers for requests.

        """
        self.api_key = api_key
        self.api_url = api_url
        self.headers = headers

    async def fetch_data_async(
        self,
        params: dict[str, Any]
    ):
        return await make_async_request(
            method='GET',
            url=self.api_url,
            params=params,
            headers=self.headers,
        )


class Account(Module):
    """
    Class with functions related to 'account' API module.
    """
    MODULE_NAME: str = 'account'

    async def get_balance(
        self,
        address: str,
        tag: str = Tag.Latest
    ) -> dict[str, Any]:
        """
        Return the Ether balance of a given address.

        https://docs.etherscan.io/api-endpoints/accounts#get-ether-balance-for-a-single-address

        Args:
            address (str): the address to check for balance
            tag (Union[str, Tag]): the pre-defined block parameter, either "earliest", "pending" or "latest". ("latest")

        Returns:
            dict[str, Any]: the dictionary with the Ether balance of the address in wei.

        """
        action_name = 'balance'
        self._check_valid_tag(tag)

        params = {
            'action': action_name,
            'address': address,
            'apiKey': self.api_key,
            'module': self.MODULE_NAME,
            'tag': tag
        }

        return await self.fetch_data_async(params)

    async def get_multi_balance(
        self,
        addresses: list[str],
        tag: str = Tag.Latest
    ) -> dict[str, Any]:
        action_name = 'balancemulti'
        self._check_valid_tag(tag)

        params = {
            'action': action_name,
            'address': addresses,
            'apiKey': self.api_key,
            'module': self.MODULE_NAME,
            'tag': tag
        }

        return await self.fetch_data_async(params)

    @api_key_required
    async def get_tx_list(
        self,
        address: str,
        startblock: int | None = None,
        endblock: int | None = None,
        page: int | None = None,
        offset: int | None = None,
        sort: str = Sort.Ascending
    ) -> dict[str, Any]:
        action_name = 'txlist'
        self._check_valid_sort(sort)

        params = {
            'module': self.MODULE_NAME,
            'action': action_name,
            'address': address,
            'startblock': startblock,
            'endblock': endblock,
            'page': page,
            'offset': offset,
            'sort': sort,
            'apiKey': self.api_key
        }

        return await self.fetch_data_async(params)

    def _check_valid_tag(self, tag: str):
        if tag not in (Tag.Latest, Tag.Earliest, Tag.Pending):
            raise exceptions.ApiException(
                '"tag" parameter have to be either "earliest", "pending" or "latest"'
            )
            
    def _check_valid_sort(self, sort: str):
        if sort not in (Sort.Ascending, Sort.Descending):
            raise exceptions.ApiException(
                '"sort" parameter have to be either "asc" or "desc"')


class Contract(Module):
    """
    Class with functions related to 'contract' API module.
    """
    MODULE_NAME: str = 'contract'

    async def get_abi(self, contract_address: str) -> dict[str, Any]:
        """
        Return the Contract Application Binary Interface (ABI) of a verified smart contract.

        https://docs.etherscan.io/api-endpoints/contracts#get-contract-abi-for-verified-contract-source-codes

        Args:
            contract_address (str): the contract address that has a verified source code.

        Returns:
            dict[str, Any]: the dictionary with the contract ABI.

        """
        action_name = 'getabi'
        params = {
            'module': self.MODULE_NAME,
            'action': action_name,
            'apiKey': self.api_key,
            'address': contract_address
        }

        response = await self.fetch_data_async(params)
        return response['result']
    
    
class Transaction(Module):
    MODULE_NAME: str = 'transaction'

    async def get_tx_status(self, tx_hash: str):
        action_name = 'getstatus'

        params = {
            'module': self.MODULE_NAME,
            'action': action_name,
            'txhash': tx_hash,
            'apikey': self.api_key,
        }
        
        return await self.fetch_data_async(params)
    

class Block(Module):
    MODULE_NAME: str = 'block'
    
    async def get_block(self, block_number: int):
        action_name = 'getblock'
        
        params = {
            'module': self.MODULE_NAME,
            'action': action_name,
            'block' : block_number,
            'apikey': self.api_key
        }
        
        return await self.fetch_data_async(params)
# endregion Components