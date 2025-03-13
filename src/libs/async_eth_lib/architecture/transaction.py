from typing import cast

from web3 import AsyncWeb3
from web3.types import TxParams, Wei, Nonce
from eth_typing import BlockIdentifier
from eth_account.datastructures import SignedTransaction
from eth_account.signers.local import LocalAccount

from .network import Network
from ..models.others import TokenAmount
from ..models.type_alias import AddressType
from ..models.transaction import Tx


class Transaction:
    def __init__(
        self, 
        account: LocalAccount,
        network: Network,
        w3: AsyncWeb3,
    ):
        self.account = account
        self.network = network
        self.w3 = w3

    @staticmethod
    async def decode_input_data():
        pass
    
    async def get_current_block_number(self) -> int:
        return await self.w3.eth.block_number

    async def get_nonce(self, address: AddressType | None = None) -> Nonce:
        """
        Get the nonce for a given Ethereum address.

        Args:
            - `address` (str | Address | ChecksumAddress | None): The Ethereum address for which to retrieve the nonce.
                If None, the address from the account manager will be used.

        Returns:
            - `int`: The nonce for the specified address.
        """
        if not address:
            address = self.account.address

        return await self.w3.eth.get_transaction_count(address) #type: ignore

    async def get_gas_price(self) -> Wei:
        """
        Get the current gas price

        Returns:
            - `Wei`: the current gas price
        """
        return await self.w3.eth.gas_price

    async def get_base_fee(self, increase_gas: float = 1.) -> Wei:
        """
        Get the current base fee

        Returns:
            - `Wei`: the current base fee
        """
        last_block = await self.w3.eth.get_block('latest')
        return Wei(last_block['baseFeePerGas'] * increase_gas) #type: ignore
        
    async def get_max_priority_fee_(
        self,
        block_number: BlockIdentifier = 'latest'
    ) -> Wei:
        """
        Get the current max priority fee

        Returns:
            - `TokenAmount`: the current max priority fee
        """
        block_data = await self.w3.eth.get_block(block_number, full_transactions=True)
        max_priority_fee_per_gas_lst = []

        for transaction in block_data.get('transactions', []):
            if isinstance(transaction, dict):
                max_priority_fee_per_gas_lst.append(
                    transaction.get('maxPriorityFeePerGas')
                )

        if len(max_priority_fee_per_gas_lst) == 0:
            max_priority_fee_per_gas = Wei(0)
        else:
            clear_list = [
                item for item in max_priority_fee_per_gas_lst
                if item
            ]
            clear_list.sort()
            max_priority_fee_per_gas = clear_list[len(
                clear_list) // 2]

        return max_priority_fee_per_gas
    

    async def get_max_priority_fee(self) -> Wei:
        """
        Get the current max priority fee

        Returns:
            - `Wei`: the current max priority fee
        """
        return await self.w3.eth.max_priority_fee

    async def get_estimate_gas(self, tx_params: TxParams) -> int:
        """
        Get the estimate gas limit for a transaction with specified parameters.

        Args:
            - `tx_params` (TxParams): parameters of the transaction.

        Returns:
            - `int`: the estimate gas.
        """
        return await self.w3.eth.estimate_gas(transaction=tx_params)
    
    async def get_tx_cost(self, gas_price_multiplier: float = 1.5) -> Wei:
        """
        Get the transaction cost

        Returns:
            - `Wei`: the transaction cost
        """
        try:
            tx_params = {
                "chainId": await self.w3.eth.chain_id,
                "from": self.account.address,
                "value": 1,
                "gasPrice": await self.get_gas_price(),
                "nonce": await self.get_nonce(),
            }

            tx_params['gas'] = await self.get_estimate_gas(tx_params) #type: ignore
        except Exception:
            tx_params['gas'] = 21_000
        return Wei(
            tx_params['gas'] 
            * tx_params['gasPrice'] 
            * gas_price_multiplier
        )

    async def auto_add_params(self, tx_params: TxParams | dict) -> TxParams | dict:
        """
        Add 'chainId', 'nonce', 'from', 'gasPrice' or 'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to
            transaction parameters if they are missing.

        Args:
            - `tx_params` (TxParams): parameters of the transaction.

        Returns:
            - `TxParams`: parameters of the transaction with added values.
        """
        if 'chainId' not in tx_params:
            tx_params['chainId'] = await self.w3.eth.chain_id

        if 'nonce' not in tx_params:
            tx_params['nonce'] = await self.get_nonce()

        if 'from' not in tx_params:
            tx_params['from'] = self.account.address

        current_gas_price = await self.get_gas_price()

        if self.network.tx_type == 2:
            tx_params['maxFeePerGas'] = tx_params.pop(
                'gasPrice', current_gas_price)

        elif 'gasPrice' not in tx_params:
            tx_params['gasPrice'] = current_gas_price

        if 'maxFeePerGas' in tx_params and 'maxPriorityFeePerGas' not in tx_params:
            tx_params['maxPriorityFeePerGas'] = (
                await self.get_max_priority_fee()
            )
            tx_params['maxFeePerGas'] += tx_params['maxPriorityFeePerGas'] #type: ignore

        multiplier_of_gas = tx_params.pop('multiplier', 1) #type: ignore

        if not tx_params.get('gas'):
            gas = await self.get_estimate_gas(cast(TxParams, tx_params))
            tx_params['gas'] = int(gas * multiplier_of_gas)

        return tx_params

    async def sign_transaction(self, tx_params: TxParams | dict) -> SignedTransaction:
        """
        Sign a transaction.

        Args:
            - `tx_params` (TxParams): parameters of the transaction.

        Returns:
            - `SignedTransaction`: the signed transaction.

        """
        return self.account.sign_transaction(tx_params)

    async def sign_message(self, message: str):
        pass

    async def sign_and_send(self, tx_params: TxParams | dict) -> Tx:
        """
        Sign and send a transaction. Additionally, add 'chainId', 'nonce', 'from', 'gasPrice' or
            'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to transaction parameters if they are missing.

        Args:
            - `tx_params` (TxParams): parameters of the transaction.

        Returns:
            - `Tx`: the instance of the sent transaction.
        """
        tx_params = await self.auto_add_params(tx_params)
        return await self.sign_and_send_prepared_tx_params(tx_params)
    
    async def sign_and_send_prepared_tx_params(self, tx_params: TxParams | dict) -> Tx:
        """
        Signs the prepared transaction parameters and sends the prepared transaction.

        Args:
            - `tx_params` (TxParams): parameters of the transaction.

        Returns:
            - `Tx`: the instance of the sent transaction.
        """
        signed_tx = await self.sign_transaction(tx_params)
        tx_hash = await self.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)

        return Tx(w3=self.w3, hash=tx_hash, params=tx_params)

    # async def find_tx_by_function_name(
    #     self,
    #     contract_address: Address | list[Address],
    #     function_name: str,
    #     address: Address | None = None,
    #     after_timestamp: int = 0,
    #     before_timestamp: int = 999_999_999_999 
    # ) -> dict[str, Any]:
    #     """
    #     Find all transactions of interaction with the contract, in addition, you can filter transactions by
    #         the name of the contract function.

    #     Args:
    #         - `contract_address` (Address | list[Address]): the contract or a list of contracts with which
    #             the interaction took place.
    #         - `function_name` (str): the function name for sorting. (any)
    #         - `address` (Address | None): the address to get the transaction list. (imported to client address)
    #         - `after_timestamp` (int): after what time to filter transactions. (0)
    #         - `before_timestamp` (int): before what time to filter transactions. (infinity)

    #     Returns:
    #         - `Dict[str, CoinTx]`: transactions found.
    #     """
    #     addresses = []
    #     if isinstance(contract_address, list):
    #         for addr in contract_address:
    #             addresses.append(addr.lower())
                
    #     else:
    #         addresses.append(contract_address.lower())
            
    #     txs = {}
        
    #     if (coin_txs := await self.network.api.account.get_tx_list(address)) is None:
    #         return {}
        
    #     for tx in coin_txs:
    #         if (
    #             after_timestamp < int(tx.get('timeStamp')) < before_timestamp
    #             and tx['result'].get('isError') == '0'
    #             and tx['result'].get('to') in addresses 
    #             and function_name in tx.get('functionName')
    #         ):
    #             txs[tx.get('hash')] = tx
        
    #     return txs
    
    # async def find_tx_by_method_id(
    #     self,
    #     contract_address: Address | list[Address],
    #     method_id: str,
    #     address: Address | None = None,
    # ) -> dict[str, Any]:
    #     """
    #     Find all transactions of interaction with the contract, in addition, you can filter transactions by
    #         the function method id

    #     Args:
    #         - `contract_address` (Address | list[Address]): the contract or a list of contracts with which
    #             the interaction took place.
    #         - `method_id` (str): the function method id to search.
    #         - `address` (Address | None): the address to get the transaction list. (imported to client address)

    #     Returns:
    #         - `Dict[str, CoinTx]`: transactions found.
    #     """
    #     txs = {}
    #     addresses = []
        
    #     if not address:
    #         address = self.account.address

    #     if isinstance(contract_address, list):
    #         for addr in contract_address:
    #             addresses.append(addr.lower())
                
    #     else:
    #         addresses.append(contract_address.lower())
        
    #     coin_txs = (await self.network.api.account.get_tx_list(address))['result']
    #     for tx in coin_txs:
    #         if (
    #             tx.get('isError') == '0'
    #             and tx.get('to') in addresses
    #             and tx.get('methodId') == method_id
    #         ):
    #             txs[tx.get('hash')] = tx
        
    #     return txs