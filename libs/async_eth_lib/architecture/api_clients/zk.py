from datetime import (
    datetime, 
    timezone
)
from typing import Any

from fake_useragent import UserAgent

from libs.async_eth_lib.utils.helpers import make_async_request


class ZkApiClient:
    """
    Class with functions related to zkSync Explorer API.
    """
    def __init__(self):
        self.api_url = 'https://block-explorer-api.mainnet.zksync.io/'
        self.docs = 'https://docs.zksync.io/build/api-reference'
        self.headers = self._init_headers()
        
        self.account = Account(self.api_url, self.headers)
        self.transaction = Transaction(self.api_url, self.headers)
        
    def _init_headers(self):
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en;q=0.9,de-DE;q=0.8,de;q=0.7,ru-RU;q=0.6,ru;q=0.5,en-US;q=0.4',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random
        }
        

# region Components
class Module:
    """
    Class with functions related to some API module.
    """
    MODULE_NAME: str = ''

    def __init__(
        self,
        api_url: str,
        headers: dict[str, Any]
    ) -> None:
        """
        Initialize the class.

        Args:
            api_url (str): an API entrypoint URL.
            headers (dict[str, Any]): a headers for requests.

        """
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


class Contract(Module):
    """
    Class with functions related to 'contract' API module.
    """
    MODULE_NAME: str = 'contract'
    
class Transaction(Module):
    MODULE_NAME: str = 'transactions'
    
    def __init__(
        self, 
        api_url: str, 
        headers: dict[str, Any]
    ):  
        api_url += self.MODULE_NAME
        super().__init__(api_url=api_url, headers=headers)
        
    async def get_txs_explorer(
        self,
        address: str, 
        page_size: int = 10,
        page: int = 1
    ) -> dict[str, Any]:
        utc_now = datetime.now(timezone.utc)
        formatted_date = utc_now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        params = {
            'address': address,
            'pageSize': page_size,
            'page': page,
            'toDate': formatted_date
        }
        
        return await self.fetch_data_async(params)
    
# endregion Components