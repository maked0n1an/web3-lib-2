from web3 import Web3
from web3.types import (
    TxParams
)
from eth_typing import ChecksumAddress
from eth_account.datastructures import (
    SignedTransaction
)
from eth_account.signers.local import LocalAccount

from libs.async_eth_lib.architecture.network import Network
from libs.async_eth_lib.models.others import TokenAmount
from libs.async_eth_lib.models.transaction import Tx


class Transaction:
    def __init__(
        self, 
        account: LocalAccount,
        network: Network,
        w3: Web3,
    ) -> None:
        self.account = account
        self.network = network
        self.w3 = w3

    @staticmethod
    async def decode_input_data():
        pass

    async def get_nonce(self, address: ChecksumAddress | None = None) -> int:
        """
        Get the nonce for a given Ethereum address.

        Args:
            address (ChecksumAddress | None): The Ethereum address for which to retrieve the nonce.
                If None, the address from the account manager will be used.

        Return:
            int: The nonce for the specified address.

        """
        if not address:
            address = self.account.address

        nonce = await self.w3.eth.get_transaction_count(address)
        return nonce

    async def get_gas_price(self) -> TokenAmount:
        """
        Get the current gas price

        Return:
            Wei 

        """
        amount = await self.w3.eth.gas_price

        return TokenAmount(
            amount=amount,
            decimals=self.network.decimals,
            wei=True
        )

    async def get_base_fee(self, increase_gas: float = 1.):
        last_block = await self.w3.eth.get_block('latest')
        return int(last_block['baseFeePerGas'] * increase_gas)

    async def get_max_priority_fee_(
        self,
        block: dict | None = None
    ) -> TokenAmount:
        """
        Get the current max priority fee

        Returns:
            Wei: the current max priority fee

        """
        if not block:
            block = await self.w3.eth.get_block('latest')

        block_number = block['number']
        latest_block_transaction_count = (
            await self.w3.eth.get_block_transaction_count(
                block_number)
        )
        max_priority_fee_per_gas_lst = []

        for i in range(latest_block_transaction_count):
            try:
                transaction = (
                    await self.w3.eth.get_transaction_by_block(
                        block_number, i
                    )
                )
                if 'maxPriorityFeePerGas' in transaction:
                    max_priority_fee_per_gas_lst.append(
                        transaction['maxPriorityFeePerGas']
                    )
            except Exception:
                continue

        if not max_priority_fee_per_gas_lst:
            # max_priority_fee_per_gas = w3.eth.max_priority_fee
            max_priority_fee_per_gas = 0
        else:
            max_priority_fee_per_gas_lst.sort()
            max_priority_fee_per_gas = max_priority_fee_per_gas_lst[len(
                max_priority_fee_per_gas_lst) // 2]

        return TokenAmount(
            amount=max_priority_fee_per_gas,
            decimals=self.network.decimals,
            wei=True
        )

    async def get_max_priority_fee(self) -> TokenAmount:
        """
        Get the current max priority fee

        Returns:
            Wei: the current max priority fee

        """
        max_priority_fee = await self.w3.eth.max_priority_fee

        return TokenAmount(
            max_priority_fee,
            decimals=self.network.decimals,
            wei=True
        )

    async def get_estimate_gas(self, tx_params: TxParams) -> TokenAmount:
        """
        Get the estimate gas limit for a transaction with specified parameters.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Wei: the estimate gas.

        """
        gas_price = await self.w3.eth.estimate_gas(transaction=tx_params)

        return TokenAmount(
            gas_price,
            decimals=self.network.decimals,
            wei=True
        )

    async def auto_add_params(self, tx_params: TxParams | dict) -> TxParams | dict:
        """
        Add 'chainId', 'nonce', 'from', 'gasPrice' or 'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to
            transaction parameters if they are missing.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            TxParams: parameters of the transaction with added values.

        """
        if 'chainId' not in tx_params:
            tx_params['chainId'] = self.network.chain_id

        if 'nonce' not in tx_params:
            tx_params['nonce'] = await self.get_nonce()

        if 'from' not in tx_params:
            tx_params['from'] = self.account.address

        is_eip_1559_tx_type = self.network.tx_type == 2
        current_gas_price = await self.get_gas_price()

        if is_eip_1559_tx_type:
            tx_params['maxFeePerGas'] = tx_params.pop(
                'gasPrice', current_gas_price.Wei)

        elif 'gasPrice' not in tx_params:
            tx_params['gasPrice'] = current_gas_price.Wei

        if 'maxFeePerGas' in tx_params and 'maxPriorityFeePerGas' not in tx_params:
            tx_params['maxPriorityFeePerGas'] = (
                await self.get_max_priority_fee()
            ).Wei
            tx_params['maxFeePerGas'] += tx_params['maxPriorityFeePerGas']

        multiplier_of_gas = tx_params.pop('multiplier', 1)

        if not tx_params.get('gas') or not int(tx_params['gas']):
            gas = await self.get_estimate_gas(tx_params=tx_params)
            tx_params['gas'] = int(gas.Wei * multiplier_of_gas)

        return tx_params

    async def sign_transaction(self, tx_params: TxParams) -> SignedTransaction:
        """
        Sign a transaction.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            SignedTransaction: the signed transaction.

        """
        signed_tx = self.account.sign_transaction(tx_params)

        return signed_tx

    async def sign_message(self, message: str):
        pass

    async def sign_and_send(self, tx_params: TxParams) -> Tx:
        """
        Sign and send a transaction. Additionally, add 'chainId', 'nonce', 'from', 'gasPrice' or
            'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to transaction parameters if they are missing.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Tx: the instance of the sent transaction.
        """
        tx_params = await self.auto_add_params(tx_params)
        return await self.sign_and_send_prepared_tx_params(tx_params)
    
    async def sign_and_send_prepared_tx_params(self, tx_params: TxParams) -> Tx:
        """
        Signs the prepared transaction parameters and sends the prepared transaction.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Tx: the instance of the sent transaction.
        """
        signed_tx = await self.sign_transaction(tx_params)
        tx_hash = await self.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)

        return Tx(tx_hash=tx_hash, params=tx_params)
