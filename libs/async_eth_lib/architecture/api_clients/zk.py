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

    def __init__(
        self,
        api_url: str = 'https://block-explorer-api.mainnet.zksync.io/',
        api_key: str = '',
        docs: str = 'https://docs.zksync.io/build/api-reference'
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.docs = docs
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'user-agent': UserAgent().chrome,
            'Ok-Access-Key': self.api_key,
        }
        # self.headers = self._init_headers()
        
        self.account = Account(self.api_url, self.headers)

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
        params: dict[str, Any],
        **kwargs
    ):
        return await make_async_request(
            method='GET',
            url=self.api_url,
            params=params,
            headers=self.headers,
            **kwargs
        )


class Account(Module):
    MODULE_NAME: str = 'address'

    async def get_txs_from_explorer(
        self,
        address: str,
        page_size: int = 10,
        page: int = 1
    ) -> dict[str, Any]:
        headers = {
            'authority': 'block-explorer-api.mainnet.zksync.io',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://explorer.zksync.io',
            'referer': 'https://explorer.zksync.io/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            
            'user-agent': UserAgent().random,
        }

        utc_now = datetime.now(timezone.utc)
        formatted_date = utc_now.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        params = {
            'address': address,
            'pageSize': page_size,
            'page': page,
            'toDate': formatted_date
        }

        return await make_async_request(
            url='https://block-explorer-api.mainnet.zksync.io/transactions',
            headers=headers,
            params=params
        )

    async def get_tx_list(
        self,
        address: str,
        page: int = 1,
        limit: int = 50,
        chain: str | None = 'zksync'
    ) -> list[dict]:
        """
        Query address transaction list information

        https://www.oklink.com/docs/en/#blockchain-general-api-address-query-address-transaction-list-information
        """

        action = 'transaction-list'

        params = {
            'chainShortName': chain,
            'address': address,
            'limit': limit,
            'page': page
        }

        res = await make_async_request(
            url=self.api_url + f'/api/v5/explorer/{self.MODULE_NAME}/{action}',
            params=params,
            headers=self.headers
        )

        return res['data'][0]['transactionLists']

    async def get_all_tx_list(
        self,
        address: str,
        chain: str | None = 'zksync'
    ) -> list[dict]:
        page = 1
        limit = 50
        txs_list = []

        txs = await self.get_tx_list(
            address, page, limit, chain
        )
        txs_list += txs
        while len(txs) == limit:
            page += 1
            txs = await self.get_tx_list(
                address, page, limit, chain
            )
            txs_list += txs
        
        return txs_list
# endregion Components
