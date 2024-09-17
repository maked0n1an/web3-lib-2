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

    def get_starknet_contract(
        self,
        address: AddressRepresentation,
        abi_or_path: str | list[str] | tuple[str] | list[dict[str, Any]] = None
    ) -> stark_Contract:
        if not abi_or_path:
            abi = read_json(path=DEFAULT_TOKEN_ABI_PATH)

        elif isinstance(abi_or_path, (list, tuple, str)):
            if all(isinstance(item, dict) for item in abi_or_path):
                abi = abi_or_path
            else:
                abi = read_json(abi_or_path)

        contract = stark_Contract(
            address=address,
            abi=abi,
            provider=self.account
        )

        return contract

    def get_token_contract(
        self,
        token: RawContract | AddressRepresentation
    ) -> stark_Contract:
        if isinstance(token, AddressRepresentation):
            address = token
            abi = None
        else:
            address = token.address
            abi = token.abi_path

        contract = self.get_starknet_contract(address, abi)

        return contract

    async def get_balance(
        self,
        token: RawContract | AddressRepresentation | None = None,
        account_address: AddressRepresentation | None = None
    ) -> TokenAmount:
        if not account_address:
            account_address = self.account.address

        if token:
            token_contract = self.get_token_contract(token=token)

            amount = (
                await (token_contract.functions['balanceOf'].call(account_address))
            )[0]
            decimals = await self.get_decimals(token)
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
        token: TokenContract | stark_Contract | AddressRepresentation
    ) -> int:
        """
        Retrieve the decimals of a token contract or token address.

        Args:
        - `token` (TokenContract | stark_Contract | AddressRepresentation): 
            The TokenContract instance, Contract instance, or token address.

        Returns:
        - `int`: The number of decimals for the token.

        """
        if isinstance(token, stark_Contract):
            return int((await token.functions['decimals'].call())[0])
        
        if getattr(token, 'decimals', None) is not None:
            return token.decimals
        
        contract = self.get_token_contract(token)
        decimals = int((await contract.functions['decimals'].call())[0])
        
        if isinstance(token, TokenContract):
            token.decimals = decimals

        return decimals
