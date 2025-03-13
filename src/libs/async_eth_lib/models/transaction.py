from typing import Any
from hexbytes import HexBytes

from web3 import Web3, AsyncWeb3
from web3.types import (
    TxReceipt,
    _Hash32,
    TxData,
    TxParams
)

from . import exceptions as exceptions
from .common import AutoRepr


# region TxArgs class
class TxArgs(AutoRepr):
    """
    An instance for named transaction arguments.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the class.

        Args:
            **kwargs: named arguments of a contract transaction.

        """
        self.__dict__.update(kwargs)

    def get_list(self) -> list[Any]:
        """
        Get list of transaction arguments.

        Returns:
            List[Any]: list of transaction arguments.

        """
        return list(self.__dict__.values())

    def get_tuple(self) -> tuple[str, Any]:
        """
        Get tuple of transaction arguments.

        Returns:
            Tuple[Any]: tuple of transaction arguments.

        """
        return tuple(self.__dict__.values())
# endregion TxArgs


# region Tx class
class Tx(AutoRepr):
    """
    An instance of transaction params for easy execution of actions on it.

    """

    def __init__(
        self,
        w3: Web3 | AsyncWeb3,
        hash: str | _Hash32,
        params: TxParams | dict
    ) -> None:
        """
        Initialize the class.

        Args:
            tx_hash (Optional[Union[str, _Hash32]]): the transaction hash. (None)
            params (Optional[dict]): a dictionary with transaction parameters. (None)

        """
        if not hash and not params:
            raise exceptions.TransactionException(
                "Specify 'tx_hash' and 'params' argument values!")

        if isinstance(hash, str):
            hash = HexBytes(hash)

        self.w3 = w3
        self.hash = hash
        self.params = params
        self.receipt = None
        self.function_identifier = None
        self.input_data = None

    async def parse_params(self) -> dict[str, Any]:
        """
        Parse the parameters of a sent transaction.

        Args:
            client (Client): the Client instance.

        Returns:
            Dict[str, Any]: the parameters of a sent transaction.

        """
        tx_data = await self.w3.eth.get_transaction(self.hash) #type: ignore
        
        if tx_data is None:
            raise exceptions.TransactionException("Transaction not found!")

        self.params = {
            'chainId': self.w3.eth.chain_id,
            'nonce': tx_data.get('nonce'),
            'gasPrice': tx_data.get('gasPrice'),
            'gas': tx_data.get('gas'),
            'from': tx_data.get('from'),
            'to': tx_data.get('to'),
            'data': tx_data.get('input'),
            'value': tx_data.get('value')
        }

        return self.params

    async def wait_for_tx_receipt(
        self,
        timeout: int | float = 120,
        poll_latency: float = 0.1
    ) -> TxReceipt:
        """
        Wait for the transaction receipt.

        Args:
            timeout (Union[int, float]): the receipt waiting timeout. (120 sec)
            poll_latency (float): the poll latency. (0.1 sec)

        Returns:
            Dict[str, Any]: the transaction receipt.

        """
        return await self.w3.eth.wait_for_transaction_receipt( #type: ignore
            transaction_hash=self.hash, timeout=timeout, poll_latency=poll_latency
        )

    async def decode_input_data(self):
        pass

    async def cancel(self):
        pass

    async def speed_up(self):
        pass
# endregion Tx class