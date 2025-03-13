import os
import random

from curl_cffi import requests
from fake_useragent import UserAgent
from web3 import AsyncWeb3
from web3.eth.async_eth import AsyncEth
from web3.middleware.geth_poa import async_geth_poa_middleware
from eth_account.signers.local import LocalAccount

from src._types.networks import NetworkNamesEnum
from .transaction import Transaction
from .contract import Contract
from .logger import CustomLogger
from ..models import exceptions as exceptions
from ..data.networks import Networks


class EvmClient:
    def __init__(
        self,
        account_id: int | str | None = None,
        private_key: str | None = None,
        network_name: str = NetworkNamesEnum.ETHEREUM,
        proxy: str | None = None,
        check_proxy: bool = True,
        create_log_file_per_account: bool = False
    ):
        self.account_id = account_id
        self.network = Networks.get_network(network_name)
        self.proxy = proxy

        self._init_proxy(check_proxy)
        self._init_headers()
        self._init_web3()
        self._init_account(private_key)
        self._init_logger(create_log_file_per_account)
        
        self.transaction = Transaction(self.account, self.network, self.w3)
        self.contract = Contract(self.transaction)

    def _init_proxy(self, check_proxy: bool):
        if not self.proxy:
            return

        if 'http' not in self.proxy:
            self.proxy = f'http://{self.proxy}'

        if check_proxy:
            your_ip = requests.get(
                url='http://eth0.me',
                proxies={'http': self.proxy, 'https': self.proxy},
                timeout=10
            ).text.rstrip()

            if your_ip not in self.proxy:
                raise exceptions.InvalidProxy(
                    f"Proxy doesn't work! It's IP is {your_ip}"
                )

    def _init_headers(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'User-Agent': UserAgent().random
        }

    def _init_web3(self):
        self.w3 = AsyncWeb3(
            AsyncWeb3.AsyncHTTPProvider(
                endpoint_uri=(
                    random.choice(self.network.rpcs)
                    if isinstance(self.network.rpcs, list)
                    else self.network.rpcs
                ),
                request_kwargs={
                    'proxy': self.proxy,
                    'headers': self.headers
                }
            ),
            modules={'eth': (AsyncEth,)},
            middlewares=[]
        )
        self.w3.middleware_onion.inject(async_geth_poa_middleware, layer=0)

    def _init_account(self, private_key: str | None):
        if private_key:
            self.account: LocalAccount = self.w3.eth.account.from_key(
                private_key=private_key
            )

        else:
            self.account: LocalAccount = self.w3.eth.account.create(
                extra_entropy=str(os.urandom(1))
            )

    def _init_logger(
        self,
        create_log_file_per_account: bool
    ) -> None:
        self.custom_logger = CustomLogger(
            account_id=self.account_id,
            address=self.account.address,
            network_name=self.network.name,
            create_log_file_per_account=create_log_file_per_account
        )
