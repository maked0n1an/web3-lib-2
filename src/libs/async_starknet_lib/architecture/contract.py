import json
from typing import Any, cast

from starknet_py.net.account.account import Account
from starknet_py.contract import (
    Contract as stark_Contract,
    AddressRepresentation
)

from src.libs.async_eth_lib.models.type_alias import AbiType

from ..data.config import DEFAULT_TOKEN_ABI_PATH
from ..models.contract import NativeTokenContract, RawContract, TokenContract
from ..models.type_alias import TokenContractType
from ..utils.helpers import read_json


class Contract:
    '''
    Important: Function "get_balance" has it's own implementation in Account class
    >>> balance = await self.account.get_balance()
    '''
    def __init__(self, account: Account):
        self.account = account

    def load_json_abi(self, abi: str) -> list[dict] | None:
        """
        Attempts to parse a string as JSON to load an ABI.

        Args:
            - `abi` (str): The ABI string to parse as JSON.

        Returns:
            - `list[dict] | None`: The parsed ABI as a list of dictionaries if valid JSON,
              None if parsing fails.
        """
        try:
            return json.loads(abi)
        except ValueError:
            return None

    def get_starknet_contract(
        self,
        address: AddressRepresentation,
        abi_or_path: AbiType
    ) -> stark_Contract:
        """
        Retrieves a Starknet contract instance from a given address and ABI or ABI path.

        Args:
            - `address` (AddressRepresentation): The address of the contract.
            - `abi_or_path` (str | list[str] | tuple[str] | list[dict[str, Any]]): The ABI or ABI path of the contract.

        Returns:
            - `stark_Contract`: The Starknet contract instance.
            
        Example:
            - `abi_or_path` (dict): {'type': 'function', 'name': 'approve', 'inputs': [{'type': 'address'}, {'type': 'uint256'}]}
            - `abi_or_path` (list[dict]): [{'type': 'function', 'name': 'approve', 'inputs': [{'type': 'address'}, {'type': 'uint256'}]}]
            - `abi_or_path` (list[str]): ['src', 'libs', 'async_eth_lib', 'abis', 'erc20.json']
            - `abi_or_path` (str): '[{"type": "function", "name": "approve", "inputs": [{"type": "address"}, {"type": "uint256"}]}]'
            - `abi_or_path` (str): 'src/libs/async_eth_lib/abis/erc20.json'
        """
        if isinstance(abi_or_path, str):
            if (json_abi := self.load_json_abi(abi_or_path)):
                abi = json_abi
            else:
                abi = read_json(abi_or_path)
        elif isinstance(abi_or_path, dict):
            abi = abi_or_path
        elif isinstance(abi_or_path, list):
            if all(isinstance(item, dict) for item in abi_or_path):
                abi = abi_or_path
            elif all(isinstance(item, str) for item in abi_or_path):
                abi = read_json(cast(list[str], abi_or_path))

        contract = stark_Contract(
            address=address,
            abi=abi, #type: ignore
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
            contract.abi_or_path
        )
    
    def get_token_starknet_contract(
        self,
        contract: TokenContractType | AddressRepresentation,
    ) -> stark_Contract:
        """
        Retrieves a Starknet token contract instance from a given address.

        Args:
            - `address` (AddressRepresentation): The address of the token contract.

        Returns:
            - `stark_Contract`: The Starknet token contract instance.
        """
        if isinstance(contract, TokenContractType):
            address = contract.address
        else:
            address = contract

        return self.get_starknet_contract(
            address=address,
            abi_or_path=DEFAULT_TOKEN_ABI_PATH
        )

    async def get_decimals(
        self,
        token: TokenContractType | AddressRepresentation | stark_Contract
    ) -> int:
        """
        Retrieve the decimals of a token contract or token address.

        Args:
            - `token` (TokenContract | NativeTokenContract | str | int | stark_Contract): The token to get decimals for. Can be:
                - A TokenContract instance
                - A NativeTokenContract instance
                - An address of the token contract
                - A Starknet contract instance

        Returns:
            - `int`: The number of decimals for the token.
        """
        if isinstance(token, TokenContract):
            if token.decimals is not None:
                return token.decimals
            
            contract = self.get_token_starknet_contract(token)
            decimals = int((await contract.functions['decimals'].call())[0])
            token.decimals = decimals
            return decimals
        
        elif isinstance(token, NativeTokenContract):
            return 18
    
        elif isinstance(token, AddressRepresentation):
            contract = self.get_token_starknet_contract(token)
            return int((await contract.functions['decimals'].call())[0])

        return int((await token.functions['decimals'].call())[0])