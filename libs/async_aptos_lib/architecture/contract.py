from typing import Any
from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient

from ..models.contract import TokenAccount


class Contract:
    def __init__(
        self,
        account: Account, 
        rest_client: RestClient
    ):
        self.account = account
        self.rest_client = rest_client
                
    async def get_decimals(
        self, 
        contract: str
    ) -> int:
        pass