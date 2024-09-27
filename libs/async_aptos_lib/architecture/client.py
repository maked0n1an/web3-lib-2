import random
import httpx

from aptos_sdk.account_address import AccountAddress
from aptos_sdk.authenticator import Authenticator, Ed25519Authenticator
from aptos_sdk.async_client import RestClient, ResourceNotFound, ApiError
from aptos_sdk.account import Account
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionPayload,
    SignedTransaction,
    RawTransaction
)
from aptos_sdk.type_tag import TypeTag, StructTag

from .contract import Account, Contract
from .logger import CustomLogger
from ..models import exceptions


class AptosClient:
    def __init__(
        self,
        account_id: int | str = None,
        private_key: str | None = None,
        proxy: str | None = None,
        check_proxy: bool = False,
        create_log_file_per_account: bool = False,
    ):
        self.account_id = account_id
        self.private_key = private_key
        self.proxy = proxy
        
        self.node_url = "https://fullnode.mainnet.aptoslabs.com/v1"
        
        self._init_proxy(check_proxy)
        self._create_client_with_proxy(proxy)
        self._init_account(private_key)
        self._init_logger(create_log_file_per_account)
        
        self.transaction = Contract(self.account, self.rest_client)
    
    def _init_account(self, private_key: str | None):
        if private_key:
            self.account = Account.load_key(private_key)

        else:
            self.account = Account.generate()
            self.private_key = self.account.private_key()
        
    def _init_proxy(self, check_proxy: bool):
        if not self.proxy:
            return

        if 'http' not in self.proxy:
            self.proxy = f'http://{self.proxy}'

        if check_proxy:
            your_ip = httpx.get(
                url='http://eth0.me',
                proxies={'http': self.proxy, 'https': self.proxy},
                timeout=10
            ).text.rstrip()

            if your_ip not in self.proxy:
                raise exceptions.InvalidProxy(
                    f"Proxy doesn't work! It's IP is {your_ip}"
                )
        
    def _create_client_with_proxy(self, proxy: str | None = None) -> None:
        if proxy:
            transport = httpx.AsyncHTTPTransport(proxy=proxy)

        self.rest_client = RestClient(
            base_url=self.node_url,
        )

        if transport:
            self.rest_client.client._transport = transport

    def _init_logger(
        self,
        create_log_file_per_account: bool
    ) -> None:
        self.custom_logger = CustomLogger(
            account_id=self.account_id,
            address=self.account.address(),
            create_log_file_per_account=create_log_file_per_account
        )

        
    
    
        