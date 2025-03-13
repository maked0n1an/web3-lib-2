import json
from typing import cast

from web3 import Web3
from web3.contract.async_contract import AsyncContract 
from web3.types import Wei, TxParams, TxReceipt

from .transaction import Transaction
from ..models.contract import NativeTokenContract, RawContract, TokenContract
from ..models.dataclasses import CommonValues, DefaultAbis
from ..models.exceptions import HTTPException
from ..models.others import TokenAmount
from ..models.type_alias import (
    AbiType,
    AddressType,
    AmountType,
    GasLimitType,
    GasPriceType,
)
from ..utils.helpers import (
    make_async_request, read_json
)


class Contract:
    def __init__(self, transaction: Transaction):
        self.transaction = transaction

    @staticmethod
    async def get_signature(hex_signature: str) -> list | None:
        """
        Find all matching signatures in the 4byte.directory database.

        Args:
            - `hex_signature` (str): A signature hash.

        Returns:
            - `list | None`: A list of matching signatures or None if none found.
        """
        try:
            url = f'https://www.4byte.directory/api/v1/signatures/?hex_signature={hex_signature}'
            response = await make_async_request(url=url)
            results = response['results']
            return [m['text_signature'] for m in sorted(results, key=lambda result: result['created_at'])]
        except HTTPException:
            return

    # @staticmethod
    # async def parse_function(text_signature: str) -> dict:
    #     """
    #     Construct a function dictionary for the ABI based on the provided text signature.

    #     Args:
    #         - `text_signature` (str): A text signature, e.g. approve(address,uint256).

    #     Returns:
    #         - `dict`: The function dictionary for the ABI.
    #     """
    #     name, sign = text_signature.split('(', 1)
    #     sign = sign[:-1]
    #     tuples = []
    #     while '(' in sign:
    #         tuple_ = text_between(text=sign[:-1], begin='(', end=')')
    #         tuples.append(tuple_.split(',') or [])
    #         sign = sign.replace(f'({tuple_})', 'tuple')

    #     inputs = sign.split(',')
    #     if inputs == ['']:
    #         inputs = []

    #     function = {
    #         'type': 'function',
    #         'name': name,
    #         'inputs': [],
    #         'outputs': [{'type': 'uint256'}]
    #     }
    #     i = 0
    #     for type_ in inputs:
    #         input_ = {'type': type_}
    #         if type_ == 'tuple':
    #             input_['components'] = [ #type: ignore
    #                 {'type': comp_type}
    #                 for comp_type in tuples[i]
    #             ]
    #             i += 1

    #         function['inputs'].append(input_)

    #     return function
        
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
    
    def get_evm_contract(
        self,
        address: AddressType,
        abi_or_path: AbiType
    ) -> AsyncContract:
        """
        Retrieves an EVM contract instance from a given address and ABI or ABI path.

        Args:
            - `address` (str | Address | ChecksumAddress): The address of the contract.
            - `abi_or_path` (str | list[dict[str, Any]]): The ABI of the contract or a path to the ABI file.

        Returns:
            - `AsyncContract`: The contract instance.

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
       
        contract = self.transaction.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi
        )

        return contract

    def get_evm_contract_from_raw(
        self,
        contract: RawContract
    ) -> AsyncContract:
        """
        Retrieves an EVM contract instance from a given RawContract object.

        Args:
            - `contract` (RawContract): The RawContract object containing the contract's address and ABI path.

        Returns:
            - `AsyncContract`: The contract instance.
        """
        return self.get_evm_contract(
            contract.address,
            contract.abi_or_path
        )

    def get_token_evm_contract(
        self,
        contract: TokenContract | AddressType,
    ) -> AsyncContract:
        """
        Retrieves an EVM token contract instance for a token contract with ERC-20 standard.

        Args:
            - `contract` (TokenContract | str | Address | ChecksumAddress): The token contract or its address.

        Returns:
            - `Contract | AsyncContract`: The contract instance for ERC-20 token.
        """
        if isinstance(contract, TokenContract):
            address = contract.address
            contract_abi = contract.abi_or_path

        else:
            address = contract
            contract_abi = DefaultAbis.ERC_20

        return self.get_evm_contract(
            address,
            contract_abi
        )

    async def approve(
        self,
        token_address: AddressType,
        tx_params: TxParams | dict,
        amount: AmountType | None = None,
        is_approve_infinity: bool = False
    ) -> TxReceipt:
        """
        Approve a spender to spend a certain amount of tokens on behalf of the user.

        Args:
            - `token_address` (str | Address | ChecksumAddress): The token address.
            - `amount` (float | int | TokenAmount | None): The amount of tokens to approve (default is None).
            - `tx_params` (TxParams | dict | None): Transaction parameters (default is None).
            - `is_approve_infinity` (bool): If True, approves an infinite amount (default is False).

        Returns:
            - `TxReceipt`: The transaction receipt.
        """
        web3_contract = self.get_token_evm_contract(token_address)

        if not amount:
            amount_wei = (
                CommonValues.InfinityInt
                if is_approve_infinity
                else await self.get_balance(token_address)
            )

        if isinstance(amount, TokenAmount):
            amount_wei = amount.Wei

        data = web3_contract.encodeABI(
            fn_name='approve',
            args=(tx_params.get('to'), amount_wei)
        )

        new_tx_params = {
            'to': token_address,
            'data': data
        }

        tx = await self.transaction.sign_and_send(tx_params=new_tx_params)
        return await tx.wait_for_tx_receipt(timeout=240)

    async def transfer(
        self,
        token_contract: TokenContract,
        receiver_address: AddressType,
        amount: AmountType | None = None,
        tx_params: TxParams | dict = {}
    ) -> TxReceipt:
        """
        Transfer tokens to a specified address.

        Args:
            - `token_contract` (TokenContract): The token contract.
            - `receiver_address` (Address): The address to receive the tokens.
            - `amount` (float | int | TokenAmount | None): The amount of tokens to transfer (default is None).
            - `tx_params` (TxParams | dict): Transaction parameters (default is empty dict).

        Returns:
            - `TxReceipt`: The transaction receipt.
        """
        web3_contract = self.get_token_evm_contract(token_contract)

        if not amount:
            amount_wei = await self.get_balance(token_contract.address)

            if token_contract.is_native_token:
                amount_wei -= await self.transaction.get_tx_cost()

        if isinstance(amount, TokenAmount):
            amount_wei = amount.Wei

        tx_params = TxParams(
            to=token_contract.address,
            data=web3_contract.encodeABI(
                fn_name='transfer',
                args=(
                    Web3.to_checksum_address(receiver_address),
                    amount_wei
                )
            )
        )

        tx = await self.transaction.sign_and_send(tx_params)
        return await tx.wait_for_tx_receipt(timeout=240)

    async def get_approved_amount(
        self,
        token_address: AddressType,
        spender_address: AddressType,
        owner_address: AddressType | None = None
    ) -> Wei:
        """
        Get the approved amount of tokens for a spender.

        Args:
            - `token_contract` (str | Address | ChecksumAddress): The token contract.
            - `spender_address` (str | Address | ChecksumAddress): The address of the spender.
            - `owner_address` (str | Address | ChecksumAddress | None): The address of the token owner (default is None).

        Returns:
            - `Wei`: The approved amount of tokens.
        """
        if not owner_address:
            owner_address = self.transaction.account.address

        web3_contract = self.get_token_evm_contract(token_address)

        amount = await web3_contract.functions.allowance(
            owner_address,
            Web3.to_checksum_address(spender_address)
        ).call()

        return amount

    async def get_balance(
        self,
        token_address: AddressType | None = None,
        account_address: AddressType | None = None
    ) -> Wei:
        """
        Get the balance of an Ethereum address.

        Args:
            - `token_address` (str | Address | ChecksumAddress | None): The token address (default is None).
            - `account_address` (str | Address | ChecksumAddress | None): The Ethereum address for which to retrieve the balance (default is None).

        Returns:
            - `Wei`: The balance of the Ethereum address.

        Note:
            - If `token_address` is provided, it retrieves the token balance.
            - If `token_address` is None, it retrieves the native token balance.
        """
        if account_address is None:
            account_address = self.transaction.account.address

        if token_address:
            web3_contract = self.get_token_evm_contract(token_address)
            return await web3_contract.functions.balanceOf(account_address).call()

        else:
            return await self.transaction.w3.eth.get_balance(account=account_address) #type: ignore

    async def get_decimals(
        self,
        token: AddressType | TokenContract | NativeTokenContract | AsyncContract
    ) -> int:
        """
        Retrieve the decimals of a token contract or token address.

        Args:
            - `token` (str | Address | ChecksumAddress | TokenContract | web3_Contract): The token to get decimals for.
                - If `token` is a `TokenContract` instance, it uses the `decimals` attribute.
                - If 'token.decimals' is None, it retrieves the decimals from the web3_contract and assigns it to the `decimals` attribute.

        Returns:
            - `int`: The number of decimals for the token
        """
        if isinstance(token, TokenContract):
            if token.decimals is not None:
                return token.decimals

            web3_contract = self.get_token_evm_contract(token)
            decimals = await web3_contract.functions.decimals().call()
            token.decimals = decimals
            return decimals

        elif isinstance(token, NativeTokenContract):
            return self.transaction.network.decimals

        elif isinstance(token, str):
            token = self.get_token_evm_contract(token)

        return await token.functions.decimals().call()  #type: ignore
        
        
    def add_multiplier_of_gas(
        self,
        tx_params: TxParams | dict,
        multiplier: float
    ) -> TxParams | dict:
        """
        Set the gas multiplier in the transaction parameters.

        Args:
            - `multiplier` (float | None): The gas multiplier to set.
            - `tx_params` (TxParams | dict): The transaction parameters.

        Returns:
            - `TxParams | dict`: The updated transaction parameters.
        """
        tx_params['gas'] = int(tx_params.get('gas', 0) * multiplier)
        return tx_params

    def set_gas_price(
        self,
        tx_params: TxParams | dict,
        gas_price: GasPriceType,
    ) -> TxParams | dict:
        """
        Set the gas limit in the transaction parameters.

        Args:
            - `gas_price` (float | int): The gas price to set.
            - `tx_params` (TxParams | dict): The transaction parameters.

        Returns:
            - `dict | TxParams`: The updated transaction parameters.
        """
        if isinstance(gas_price, float | int):
            gas_price = TokenAmount(
                amount=gas_price,
                decimals=self.transaction.network.decimals,
                set_gwei=True
            )
        tx_params['gasPrice'] = Wei(gas_price.GWei)
        return tx_params

    def set_gas_limit(
        self,
        tx_params: dict | TxParams,
        gas_limit: GasLimitType,
    ) -> dict | TxParams:
        """
        Set the gas limit in the transaction parameters.

        Args:
            - `gas_limit` (int | TokenAmount): The gas limit to set.
            - `tx_params` (dict | TxParams): The transaction parameters.

        Returns:
            - `dict | TxParams`: The updated transaction parameters.
        """
        if isinstance(gas_limit, int):
            gas_limit = TokenAmount(
                amount=gas_limit,
                decimals=self.transaction.network.decimals,
                is_wei=True
            )
        tx_params['gas'] = gas_limit.Wei
        return tx_params
