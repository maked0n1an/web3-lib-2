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

from .transaction import Transaction
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

    @staticmethod
    def get_checksum_address(
        address: ParamsTypes.Address
    ) -> ChecksumAddress:
        """
        Convert an address to its checksummed format.

        Args:
            address (ParamsTypes.Address): The address to checksum.

        Returns:
            ChecksumAddress: The checksummed address.
        """
        return Web3.to_checksum_address(address)

    @staticmethod
    async def get_signature(hex_signature: str) -> list | None:
        """
        Find all matching signatures in the 4byte.directory database.

        Args:
            hex_signature (str): A signature hash.

        Returns:
            list | None: A list of matching signatures or None if none found.
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
        Construct a function dictionary for the ABI based on the provided text signature.

        Args:
            text_signature (str): A text signature, e.g. approve(address,uint256).

        Returns:
            dict: The function dictionary for the ABI.
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
    
    def get_evm_contract(
        self,
        address: ParamsTypes.Address,
        abi_or_path: str | list[dict[str, Any]]
    ) -> web3_Contract | web3_AsyncContract:
        """
        Retrieves an EVM contract instance from a given address and ABI or ABI path.

        Args:
            address (ParamsTypes.Address): The address of the contract.
            abi_or_path (str | list[dict[str, Any]]): The ABI of the contract or a path to the ABI file.

        Returns:
            Contract | AsyncContract: The contract instance.
        """
        address = Contract.get_checksum_address(address)
        abi = self.get_abi(abi_or_path)
        
        address = self.transaction.w3.eth.contract(
            address=address,
            abi=abi
        )

        return address
    
    def get_evm_contract_from_raw(
        self,
        contract: RawContract
    ) -> web3_Contract | web3_AsyncContract:
        """
        Retrieves an EVM contract instance from a given RawContract object.

        Args:
            contract (RawContract): The RawContract object containing the contract's address and ABI path.

        Returns:
            Contract | AsyncContract: The contract instance.
        """
        return self.get_evm_contract(contract.address, contract.abi_path)
    
    def get_token_evm_contract(
        self,
        contract: RawContract | ParamsTypes.Address,
        abi_or_path: str | tuple | list[dict[str, Any]] = None
    ) -> web3_Contract | web3_AsyncContract:
        """
        Retrieves an EVM contract instance for a token contract.

        This method can handle both RawContract objects and direct addresses. 
        It attempts to use the ABI path from the RawContract if provided, 
        otherwise falls back to the default ABI path for tokens.

        Args:
            contract (RawContract | str | Address | ChecksumAddress | ENS): The token contract, contract instance, or address.
            abi_or_path (str | tuple | list[dict[str, Any]] | None): The ABI or path to the ABI file. Defaults to None.

        Returns:
            Contract | AsyncContract: The contract instance.
        """
        if isinstance(contract, RawContract):
            address = contract.address
            abi_path = (
                contract.abi_path or abi_or_path or DefaultAbis.Token
            )
            
        else:
            address = contract
            abi_path = abi_or_path or DefaultAbis.Token
        
        return self.get_evm_contract(address, abi_path)

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
            TxReceipt: The transaction receipt.
        """
        web3_contract = self.get_token_evm_contract(token_contract)
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
        """
        Transfer tokens to a specified address.

        Args:
            receiver_address (ParamsTypes.Address): The address to receive the tokens.
            token (TokenContract | ParamsTypes.Address | None): The token contract or address (default is None).
            amount (ParamsTypes.Amount | None): The amount of tokens to transfer (default is None).
            tx_params (TxParams | dict): Transaction parameters (default is empty dict).

        Returns:
            TxReceipt: The transaction receipt.
        """
        receiver = Contract.get_checksum_address(receiver_address)
        contract = self.get_token_evm_contract(token)

        if not amount:
            amount = await self.get_balance(token)

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

    async def get_approved_amount(
        self,
        token_contract: RawContract | ParamsTypes.Address,
        spender_address: ParamsTypes.Address,
        owner: ParamsTypes.Address | None = None
    ) -> TokenAmount:
        """
        Get the approved amount of tokens for a spender.

        Args:
            token_contract (RawContract | ParamsTypes.Address): The token contract or address.
            spender_address (ParamsTypes.Address): The address of the spender.
            owner (ParamsTypes.Address | None): The address of the token owner (default is None).

        Returns:
            TokenAmount: The approved amount of tokens.
        """
        if not owner:
            owner = self.transaction.account.address
            
        spender_address = Contract.get_checksum_address(spender_address)
        web3_contract = self.get_token_evm_contract(token_contract)

        amount = await web3_contract.functions.allowance(
            owner,
            spender_address,
        ).call()
        decimals = await self.get_decimals(web3_contract)

        return TokenAmount(amount, decimals, wei=True)

    async def get_balance(
        self,
        token: RawContract | ParamsTypes.Web3Contract | ParamsTypes.Address | None = None,
        address: ParamsTypes.Address | None = None
    ) -> TokenAmount:
        """
        Get the balance of an Ethereum address.

        Args:
            token (RawContract | ParamsTypes.Web3Contract | ParamsTypes.Address | None): The token contract or address (default is None).
            address (ParamsTypes.Address | None): The Ethereum address for which to retrieve the balance (default is None).

        Returns:
            TokenAmount: An object representing the token balance, including the amount and decimals.

        Note:
            If `token_contract` is provided, it retrieves the token balance.
            If `token_contract` is None, it retrieves the native token balance.
        """
        if not address:
            address = self.transaction.account.address
            
        if token is None:
            amount = await self.transaction.w3.eth.get_balance(account=address)
            decimals = self.transaction.network.decimals

        elif type(token) in ParamsTypes.Web3Contract.__args__:
            amount = await token.functions.balanceOf(address).call()
            decimals = await self.get_decimals(token)
            
        else:
            web3_contract = self.get_token_evm_contract(token)
            amount = await web3_contract.functions.balanceOf(address).call()
            decimals = await self.get_decimals(token)
        
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
            token (RawContract | ParamsTypes.TokenContract | ParamsTypes.Web3Contract): The token contract address or contract instance.

        Returns:
        - `int`: The number of token decimals.
        """
        if isinstance(contract, ParamsTypes.Web3Contract):
            return await contract.functions.decimals().call()

        if getattr(contract, 'decimals', None) is not None:
            return contract.decimals

        web3_contract = self.get_token_evm_contract(contract)
        decimals = await web3_contract.functions.decimals().call()

        if isinstance(contract, TokenContract):
            contract.decimals = decimals

        return decimals

    def add_multiplier_of_gas(
        self,
        tx_params: TxParams | dict,
        multiplier: float | None = None
    ) -> TxParams | dict:
        """
        Set the gas multiplier in the transaction parameters.

        Args:
            multiplier (float | None): The gas multiplier to set.
            tx_params (TxParams | dict): The transaction parameters.

        Returns:
            TxParams | dict: The updated transaction parameters.
        """
        tx_params['multiplier'] = multiplier
        return tx_params

    def set_gas_price(
        self,
        gas_price: ParamsTypes.GasPrice,
        tx_params: TxParams | dict,
    ) -> TxParams | dict:
        """
        Set the gas limit in the transaction parameters.

        Args:
            gas_limit (ParamsTypes.GasLimit): The gas limit to set.
            tx_params (dict | TxParams): The transaction parameters.

        Returns:
            dict | TxParams: The updated transaction parameters.
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
