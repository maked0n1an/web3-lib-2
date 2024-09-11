from functools import lru_cache
from typing import Any

from starknet_py.net.account.account import Account
from starknet_py.contract import (
    Contract as stark_Contract,
    AddressRepresentation
)

from ..data.config import DEFAULT_TOKEN_ABI_PATH
from ..models.contract import RawContract, TokenContract
from ..models.others import TokenAmount
from ..utils.helpers import read_json


class Contract:
    def __init__(self, account: Account):
        self.account = account
        
    def get_abi(
        self,
        abi_or_path: list | tuple | str | list[dict]
    ) -> list[dict] | None:
        if not isinstance(abi_or_path, (list, tuple, str)):
            return None
        
        if all(isinstance(item, dict) for item in abi_or_path):
            return abi_or_path
        else:
            return read_json(abi_or_path)

    async def get_starknet_contract(
        self,
        address: AddressRepresentation,
        abi_or_path: str | list[str] | tuple[str] | list[dict[str, Any]] = None
    ) -> stark_Contract:
        abi = self.get_abi(abi_or_path)

        contract = stark_Contract(
            address=address,
            abi=abi if abi else read_json(DEFAULT_TOKEN_ABI_PATH),
            provider=self.account
        )

        return contract

    async def get_token_contract(
        self,
        token: RawContract | AddressRepresentation
    ) -> stark_Contract:
        if isinstance(token, AddressRepresentation):
            address = token
            abi = None
        else:
            address = token.address
            abi = token.abi_path

        contract = await self.get_starknet_contract(address, abi)

        return contract

    async def get_balance(
        self,
        token: RawContract | AddressRepresentation | None = None,
        account_address: AddressRepresentation | None = None
    ) -> TokenAmount:
        if not account_address:
            account_address = self.account.address

        if token:
            token_contract = await self.get_token_contract(token=token)

            amount = (
                await (token_contract.functions['balanceOf'].call(account_address))
            )[0]
            decimals = await self.get_decimals(contract=token_contract)
        else:
            amount = await self.account.get_balance()
            decimals = 18

        return TokenAmount(
            amount=amount,
            decimals=decimals,
            wei=True
        )

    async def get_decimals(
        self,
        contract: TokenContract | stark_Contract | None = None
    ) -> int:
        """
        Retrieve the decimals of a token contract or token address.

        Args:
        - `token` (TokenContract | stark_Contract): 
            The TokenContract instance or Contract instance.

        Returns:
        - `int`: The number of token decimals.
        """
        if isinstance(contract, stark_Contract):
            return int((await contract.functions['decimals'].call())[0])
        
        if getattr(contract, 'decimals', None) is not None:
            return contract.decimals
        
        stark_contract = stark_Contract(
            address=contract.address,
            abi=contract.abi_path,
            provider=self.account
        )
        decimals = int((await stark_contract.functions['decimals'].call())[0])
        
        if isinstance(contract, TokenContract):
            contract.decimals = decimals

        return decimals
