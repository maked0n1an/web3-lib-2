import random
from typing import List

import libs.async_eth_lib.models.exceptions as exceptions
from libs.async_eth_lib.models.contract import TokenContract
from libs.async_eth_lib.models.others import TokenAmount
from libs.async_eth_lib.architecture.network import Network
from libs.async_eth_lib.data.networks import Networks


# region Class to get info about operations like swap, add liquidity, remove liquidity etc.
class OperationInfo:
    def __init__(
        self,
        from_token_name: str = None,
        to_token_name: str = None,
        slippage: float = 0.5,
        from_network: Network = Networks.Goerli,
        to_network: Network | None = None,
        amount: float | None = None,
        amount_from: float = 0.0,
        amount_to: float | None = None,
        ndigits: int = 5,
        min_percent: float = 0.0,
        max_percent: float = 100.0,
        gas_price: float | None = None,
        gas_limit: int | None = None,
        multiplier_of_gas: float | None = None
    ) -> None:
        """
        Initialize the OperationInfo class.

        Args:
            from_token_name (str): The token to swap from.
            to_token_name (str): The token to swap to.
            slippage (float): The slippage tolerance (default is 0.5).
            from_network (Network | None): The source network for the swap (default is None).
            to_network (Network | None): The destination network for the swap (default is None).
            amount (float | None): The amount to swap (default is None).
            amount_from (float | None): The minimum amount for random amount generation.
            amount_to (float | None): The maximum amount for random amount generation.
            ndigits (int): The number of digits places for random amount generation (default is 5).
            min_percent (int | None): The minimum percentage for random amount generation.
            max_percent (int | None): The maximum percentage for random amount generation.
            multiplier_of_gas (int | None): A multiplier for gas calculation (default is None).
            gas_price (float | None): Gas price for the transaction (default is None).
            gas_limit (int | None): Gas limit for the transaction (default is None).

        """
        self.from_token_name = from_token_name
        self.to_token_name = to_token_name
        self.from_network = from_network
        self.to_network = to_network
        self.amount = amount
        self.slippage = slippage
        self.amount_by_percent = 0
        self.gas_price = gas_price
        self.gas_limit = gas_limit
        self.multiplier_of_gas = multiplier_of_gas
        if amount_to:
            self.amount = self._get_random_amount(
                amount_from, amount_to, ndigits)
        if max_percent:
            self.amount_by_percent = self._get_random_amount_by_percent(
                min_percent, max_percent, ndigits
            )

    def _get_random_amount(
        self, 
        amount_from: float, 
        amount_to: float, 
        ndigits: int
    ) -> float:
        random_value = random.uniform(amount_from, amount_to)
        return round(random_value, ndigits)

    def _get_random_amount_by_percent(
        self, 
        min_percent: int, 
        max_percent: int,
        ndigits: int
    ) -> float:
        random_percent_amount = random.uniform(min_percent, max_percent) / 100
        return round(random_percent_amount, ndigits)
# endregion Class to get info about swap


# region Class to prepare data for swap/bridge/deposit/borrow etc.
class OperationProposal:
    def __init__(
        self,
        from_token: TokenContract,
        amount_from: TokenAmount,
        to_token: TokenContract | None = None,
        min_amount_to: TokenAmount | None = None
    ) -> None:
        """
        Initialize the SwapQuery class.

        Args:
            from_token (TokenContract): The contract of the token to swap from.
            amount_from (TokenAmount): The amount of the from token.
            to_token (TokenContract | None): The contract of the token to swap to (default is None).
            min_amount_to (TokenAmount | None): The minimum amount of the to token (default is None).

        """
        self.from_token = from_token
        self.to_token = to_token
        self.amount_from = amount_from
        self.min_amount_to = min_amount_to
# endregion Class to prepare swap


# region TxPayloads details
class TxPayloadDetails:
    def __init__(
        self,
        method_name: str,
        addresses: List[str],
        function_signature: str | None = None,
        bool_list: List[bool] | None = None
    ):
        """
        Initialize the RouteInfo class.

        Args:
            method_name (str): The name of the method.
            addresses (List[str]): The list of addresses.
            function_signature (str | None): The hex signature of provided function.
            bool_list (List[bool] | None): The list of boolean values (default is None).

        """
        self.method_name = method_name
        self.swap_path = addresses
        if function_signature:
            self.function_signature = function_signature
        if bool_list:
            self.bool_list = bool_list
            
class TxPayloadDetailsFetcher:
    PATHS: dict[str, dict[str: TxPayloadDetails]] = {}

    @classmethod
    def get_tx_payload_details(
        cls,
        first_token: str,
        second_token: str
    ) -> TxPayloadDetails:
        first_token = first_token.upper()
        second_token = second_token.upper()

        if first_token not in cls.PATHS:
            raise exceptions.TxPayloadDetailsNotAdded(
                f"The '{first_token}' token has not been "
                f"added to {cls.__name__} PATHS dict"
            )

        available_token_routes = cls.PATHS[first_token]

        if second_token not in available_token_routes:
            raise exceptions.TxPayloadDetailsNotAdded(
                f"The '{second_token}' as second token has not been "
                f"added to {cls.__name__} {first_token} PATHS dict"
            )

        return available_token_routes[second_token]
# endregion TxPayloads details