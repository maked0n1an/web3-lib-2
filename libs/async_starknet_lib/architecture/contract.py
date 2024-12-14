from typing import Any

from starknet_py.net.account.account import Account
from starknet_py.contract import (
    Contract as stark_Contract,
    AddressRepresentation
)

from ..data.config import DEFAULT_TOKEN_ABI_PATH
from ..models.contract import RawContract, TokenContract
from ..utils.helpers import read_json


class Contract:
    '''
    Important: Function "get_balance" has it's own implementation in Account class
    >>> balance = await self.account.get_balance()
    '''
    def __init__(self, account: Account):
        self.account = account

    def get_abi(
        self,
        abi_or_path: str | tuple | list[dict]
    ) -> list[dict]:
        """
        Retrieve the ABI from a given path or return the default ABI.

        Args:
            abi_or_path (list | tuple | str | list[dict] | None): The ABI or path to the ABI.

        Returns:
            list[dict] | None: The ABI as a list of dictionaries or None if not found.
        """
        if all(isinstance(item, dict) for item in abi_or_path):
            return abi_or_path
        else:
            return read_json(abi_or_path)

    def get_starknet_contract(
        self,
        address: AddressRepresentation,
        abi_or_path: str | list[str] | tuple[str] | list[dict[str, Any]]
    ) -> stark_Contract:
        """
        Retrieves a Starknet contract instance from a given address and ABI or ABI path.

        Args:
            - `address` (AddressRepresentation): The address of the contract.
            - `abi_or_path` (str | list[str] | tuple[str] | list[dict[str, Any]]): The ABI or ABI path of the contract.

        Returns:
            - `stark_Contract`: The Starknet contract instance.
        """
        contract = stark_Contract(
            address=address,
            abi=self.get_abi(abi_or_path),
            provider=self.account
        )

        return contract

    def get_starknet_contract_from_raw(
        self,
        contract: RawContract
    ) -> stark_Contract:
        """
        Retrieves a Starknet contract instance from a given RawContract object.

        Args:
            - `contract` (RawContract): The RawContract object containing the contract's address and ABI path.

        Returns:
            - `stark_Contract`: The Starknet contract instance.
        """
        return self.get_starknet_contract(
            contract.address, 
            contract.abi_path
        )
    
    def get_token_starknet_contract(
        self,
        contract: TokenContract | AddressRepresentation,
    ) -> stark_Contract:
        """
        Retrieves a Starknet token contract instance from a given address.

        Args:
            - `address` (AddressRepresentation): The address of the token contract.

        Returns:
            - `stark_Contract`: The Starknet token contract instance.
        """
        if isinstance(contract, TokenContract):
            address = contract.address
            abi_or_path = contract.abi_path

        else:
            address = contract
            abi_or_path = DEFAULT_TOKEN_ABI_PATH

        return self.get_starknet_contract(
            address=address,
            abi_or_path=abi_or_path
        )

    async def get_decimals(
        self,
        token: AddressRepresentation | TokenContract | stark_Contract | None = None
    ) -> int:
        """
        Retrieve the decimals of a token contract or token address.

        Args:
            - `token` (str | int | TokenContract | stark_Contract): The token to get decimals for. Can be:
                - An address of the token contract
                - A tokenContract instance
                - A starknet contract instance

        Returns:
            - `int`: The number of decimals for the token.
        """
        if not token:
            return 18
        
        if isinstance(token, TokenContract):
            if getattr(token, 'decimals', None) is not None:
                return token.decimals
            
            contract = self.get_token_starknet_contract(token)
            decimals = int((await contract.functions['decimals'].call())[0])
            token.decimals = decimals
            return decimals
    
        if isinstance(token, AddressRepresentation):
            contract = self.get_token_starknet_contract(token)
            return int((await contract.functions['decimals'].call())[0])

        return int((await token.functions['decimals'].call())[0])
