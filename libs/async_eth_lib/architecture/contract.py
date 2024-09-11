from functools import lru_cache
from typing import Any

from web3 import Web3
from web3.types import (
    TxParams,
    TxReceipt,
)
from web3.contract import (
    Contract as web3_Contract,
    AsyncContract as web3_AsyncContract
)
from eth_typing import ChecksumAddress

from ..architecture.transaction import Transaction
from ..models.contract import RawContract, TokenContract
from ..models.dataclasses import (
    CommonValues, DefaultAbis
)
from ..models.others import ParamsTypes, TokenAmount
from ..models.transaction import TxArgs
from ..utils.helpers import (
    make_async_request, read_json, text_between
)


class Contract:
    def __init__(self, transaction: Transaction):
        self.transaction = transaction

    @lru_cache(maxsize=128)
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

    def get_web3_contract(
        self,
        address: ParamsTypes.Address,
        abi_or_path: str | list[dict[str, Any]] | None
    ) -> web3_Contract | web3_AsyncContract:
        abi = self.get_abi(abi_or_path)

        contract = self.transaction.w3.eth.contract(
            address=address,
            abi=abi if abi else DefaultAbis.Token
        )

        return contract

    @staticmethod
    def get_checksum_address(
        address: ParamsTypes.Address
    ) -> ChecksumAddress:
        return Web3.to_checksum_address(address)

    @staticmethod
    async def get_signature(hex_signature: str) -> list | None:
        """
        Find all matching signatures in the database of https://www.4byte.directory/.

        :param str hex_signature: a signature hash.
        :return list | None: matches found.
        """
        try:
            url = f'https://www.4byte.directory/api/v1/signatures/?hex_signature={hex_signature}'
            response = await make_async_request(method="GET", url=url)
            results = response['results']
            return [m['text_signature'] for m in sorted(results, key=lambda result: result['created_at'])]
        except:
            return

    @staticmethod
    async def parse_function(text_signature: str) -> dict:
        """
        Construct a function dictionary for the Application Binary Interface (ABI) based on the provided text signature.

        :param str text_signature: a text signature, e.g. approve(address,uint256).
        :return dict: the function dictionary for the ABI.
        """
        name, sign = text_signature.split('(', 1)
        sign = sign[:-1]
        tuples = []
        while '(' in sign:
            tuple_ = text_between(text=sign[:-1], begin='(', end=')')
            tuples.append(tuple_.split(',') or [])
            sign = sign.replace(f'({tuple_})', 'tuple')

        inputs = sign.split(',')
        if inputs == ['']:
            inputs = []

        function = {
            'type': 'function',
            'name': name,
            'inputs': [],
            'outputs': [{'type': 'uint256'}]
        }
        i = 0
        for type_ in inputs:
            input_ = {'type': type_}
            if type_ == 'tuple':
                input_['components'] = [{'type': comp_type}
                                        for comp_type in tuples[i]]
                i += 1

            function['inputs'].append(input_)

        return function

    @staticmethod
    async def get_contract_attributes(
        contract: RawContract | ParamsTypes.Address
    ) -> tuple[ChecksumAddress, list[str] | tuple[str] | str | None]:
        """
        Get the checksummed contract address and path to ABI file.

        Args:
            contract (TokenContract | Contract | Address): The contract address or instance.

        Returns:
            tuple[ChecksumAddress, list | None]: The checksummed contract address and path to ABI file.

        """
        abi_path = None
        address = None
        if type(contract) in ParamsTypes.Address.__args__:
            address = contract
        else:
            address, abi_path = contract.address, contract.abi_path

        return Contract.get_checksum_address(address), abi_path

    async def approve(
        self,
        token_contract: RawContract | ParamsTypes.Address,
        tx_params: TxParams | dict,
        amount: ParamsTypes.Amount | None = None,
        is_approve_infinity: bool = False
    ) -> TxReceipt:
        """
        Approve a spender to spend a certain amount of tokens on behalf of the user.

        Args:
            token_contract (RawContract | str | Address | ChecksumAddress | ENS): The token contract, contract instance, or address.
            amount (float | int | TokenAmount | None): The amount of tokens to approve (default is None).
            tx_params (TxParams | dict | None): Transaction parameters (default is None).
            is_approve_infinity (bool): If True, approves an infinite amount (default is False).

        Returns:
            Tx: The transaction params object.
        """
        web3_contract = await self.get(token_contract)
        spender_address = Contract.get_checksum_address(tx_params['to'])

        if not amount:
            amount = (
                CommonValues.InfinityInt
                if is_approve_infinity
                else await self.get_balance(token=web3_contract)
            )

        elif isinstance(amount, (int, float)):
            decimals = await self.get_decimals(contract=token_contract)
            token_amount = TokenAmount(amount=amount, decimals=decimals).Wei

        else:
            token_amount = amount.Wei

        data = web3_contract.encodeABI(
            'approve',
            args=TxArgs(
                spender=spender_address,
                amount=token_amount
            ).get_tuple()
        )

        keys_to_include = [
            'gas', 'gasPrice', 'multiplier', 'maxPriorityFeePerGas'
        ]

        if tx_params:
            new_tx_params = {key: tx_params[key]
                             for key in keys_to_include if key in tx_params}
        else:
            new_tx_params = {}

        new_tx_params.update({
            'to': token_contract.address,
            'data': data
        })

        tx = await self.transaction.sign_and_send(tx_params=new_tx_params)
        return await tx.wait_for_tx_receipt(
            web3=self.transaction.w3,
            timeout=240
        )

    async def transfer(
        self,
        receiver_address: ParamsTypes.Address,
        token: TokenContract | ParamsTypes.Address = None,
        amount: ParamsTypes.Amount | None = None,
        tx_params: TxParams | dict = {},
    ) -> TxReceipt:
        receiver = Contract.get_checksum_address(receiver_address)
        contract = await self.get(contract=token)

        if not amount:
            amount = await self.get_balance(token)
        if not amount: 
            return False

        if isinstance(amount, float | int):
            amount = TokenAmount(
                amount=amount,
                decimals=await self.get_decimals(token)
            )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                fn_name='transfer',
                args=(receiver, amount.Wei)
            )
        )

        tx = await self.transaction.sign_and_send(tx_params)
        receipt = await tx.wait_for_tx_receipt(
            web3=self.transaction.w3,
            timeout=300
        )
        return receipt

    async def get(
        self,
        contract: RawContract | ParamsTypes.Address,
        abi_or_path: str | list[dict[str, Any]] | None = None
    ) -> web3_Contract | web3_AsyncContract:
        """
        Get a contract instance.

        Args:
            contract (RawContract | Address | ChecksumAddress | str): the contract address or instance.
            abi (list | str | None, optional): the contract ABI

        Returns:
            AsyncContract | Contract: the contract instance.
        """

        contract_address, contract_abi_path = await self.get_contract_attributes(
            contract=contract
        )

        if not contract_abi_path:
            # # todo: сделаем подгрузку abi из эксплорера (в том числе через proxy_address)
            # raise ValueError("Can not get contract ABI")
            contract_abi_path = abi_or_path

        return self.get_web3_contract(
            address=contract_address,
            abi_or_path=contract_abi_path
        )

    async def get_approved_amount(
        self,
        token_contract: RawContract | ParamsTypes.Address,
        spender_address: ParamsTypes.Address,
        owner: ParamsTypes.Address | None = None
    ) -> TokenAmount:
        """
        Get the approved amount of tokens for a spender.

        Args:
            token_contract (Contract | Address): The token contract or address.
            spender_address (Address): The address of the spender.
            owner (Address | None): The address of the token owner (default is None).

        Returns:
            TokenAmount: The approved amount of tokens.
        """
        spender_address = Contract.get_checksum_address(spender_address)

        if not owner:
            owner = self.transaction.account.address

        web3_contract = await self.get(contract=token_contract)

        amount = await web3_contract.functions.allowance(
            owner,
            spender_address,
        ).call()
        decimals = await self.get_decimals(contract=token_contract)

        return TokenAmount(amount, decimals, wei=True)

    async def get_balance(
        self,
        token: RawContract | ParamsTypes.Web3Contract | ParamsTypes.Address | None = None,
        address: ParamsTypes.Address | None = None
    ) -> TokenAmount:
        """
        Get the balance of an Ethereum address.

        Args:
            token_contract (RawContract | Contract | Async_Contract | Address | ChecksumAddress | str | None):
                The token contract, contract address, or None for ETH balance.
            address (Address, ChecksumAddress, str | None): The Ethereum address for which to retrieve the balance.

        Returns:
            TokenAmount: An object representing the token balance, including the amount and decimals.

        Note:
            If `token_contract` is provided, it retrieves the token balance.
            If `token_contract` is None, it retrieves the native token balance.
        """
        if not address:
            address = self.transaction.account.address

        if isinstance(token, ParamsTypes.TokenContract):
            web3_contract = await self.get(contract=token)
            amount = await web3_contract.functions.balanceOf(address).call()
            decimals = await self.get_decimals(contract=token)

        elif isinstance(token, ParamsTypes.Web3Contract):
            amount = await token.functions.balanceOf(address).call()
            decimals = await self.get_decimals(contract=token)

        elif (
            isinstance(token, RawContract)
            or type(token) in ParamsTypes.Address.__args__
        ):
            web3_contract = await self.get(contract=token)
            amount = await web3_contract.functions.balanceOf(address).call()
            decimals = await self.get_decimals(contract=web3_contract)

        else:
            amount = await self.transaction.w3.eth.get_balance(account=address)
            decimals = self.transaction.network.decimals

        return TokenAmount(
            amount=amount,
            decimals=decimals,
            wei=True
        )

    async def get_decimals(
        self,
        contract: RawContract | ParamsTypes.TokenContract | ParamsTypes.Web3Contract
    ) -> int:
        """
        Retrieve the decimals of a token contract or contract.

        Args:
        - `token_contract` (TokenContract | NativeTokenContract | RawContract | AsyncContract | Contract): 
            The token contract address or contract instance.

        Returns:
        - `int`: The number of token decimals.
        """
        if isinstance(contract, ParamsTypes.Web3Contract):
            return await contract.functions.decimals().call()

        if getattr(contract, 'decimals', None) is not None:
            return contract.decimals

        web3_contract = self.get_web3_contract(
            address=contract.address,
            abi_or_path=contract.abi_path
        )
        decimals = await web3_contract.functions.decimals().call()

        if isinstance(contract, TokenContract):
            contract.decimals = decimals

        return decimals

    def add_multiplier_of_gas(
        self,
        tx_params: TxParams | dict,
        multiplier: float | None = None
    ) -> TxParams | dict:
        tx_params['multiplier'] = multiplier
        return tx_params

    def set_gas_price(
        self,
        gas_price: ParamsTypes.GasPrice,
        tx_params: TxParams | dict,
    ) -> TxParams | dict:
        """
        Set the gas price in the transaction parameters.

        Args:
            gas_price (GWei): The gas price to set.
            tx_params (TxParams | dict): The transaction parameters.

        Returns:
            TxParams | dict: The updated transaction parameters.

        """
        if isinstance(gas_price, float | int):
            gas_price = TokenAmount(
                amount=gas_price,
                decimals=self.transaction.network.decimals,
                set_gwei=True
            )
        tx_params['gasPrice'] = gas_price.GWei
        return tx_params

    def set_gas_limit(
        self,
        gas_limit: ParamsTypes.GasLimit,
        tx_params: dict | TxParams,
    ) -> dict | TxParams:
        """
        Set the gas limit in the transaction parameters.

        Args:
            gas_limit (int | TokenAmount): The gas limit to set.
            tx_params (dict | TxParams): The transaction parameters.

        Returns:
            dict | TxParams: The updated transaction parameters.

        """
        if isinstance(gas_limit, int):
            gas_limit = TokenAmount(
                amount=gas_limit,
                decimals=self.transaction.network.decimals,
                wei=True
            )
        tx_params['gas'] = gas_limit.Wei
        return tx_params
