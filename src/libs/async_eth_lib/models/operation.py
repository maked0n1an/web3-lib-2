import random
from typing import List, TypedDict
from typing_extensions import NotRequired

from src._types.networks import NetworkNamesEnum
from src._types.tokens import TokenSymbol

from . import exceptions as exceptions
from .contract import NativeTokenContract, TokenContract
from .others import TokenAmount


# region Class to get info about operations like swap, bridge, add liquidity, remove liquidity etc.
class OperationInfo:
    def __init__(
        self,
        from_token_name: TokenSymbol,
        to_token_name: TokenSymbol,
        slippage: float = 0.5,
        to_network: NetworkNamesEnum = NetworkNamesEnum.ETH_GOERLI,
        amount: float = 0,
        amount_from: float = 0,
        amount_to: float | None = None,
        ndigits: int = 5,
        min_percent: float = 0,
        max_percent: float = 100,
        gas_price: float | None = None,
        gas_limit: int | None = None,
        multiplier_of_gas: float | None = None
    ):
        """
        Initialize the OperationInfo class.

        Args:
            from_token_name (TokenSymbol): The token to swap from.
            to_token_name (TokenSymbol): The token to swap to.
            slippage (float): The slippage tolerance (default is 0.5).
            to_network_name (NetworkNames | None): The destination network name (default is Goerli).
            amount (float | None): The amount to swap (default is None).
            amount_from (float | None): The minimum amount for random amount generation.
            amount_to (float | None): The maximum amount for random amount generation.
            ndigits (int): The number of digits places for random amount generation (default is 5).
            min_percent (float): The minimum percentage for random amount generation. Default is 0.
            max_percent (float): The maximum percentage for random amount generation. Default is 100.
            multiplier_of_gas (int | None): A multiplier for gas calculation (default is None).
            gas_price (float | None): Gas price for the transaction (default is None).
            gas_limit (int | None): Gas limit for the transaction (default is None).

        """
        self.from_token_symbol = from_token_name
        self.to_token_symbol = to_token_name
        self.to_network_name = to_network
        self.amount = abs(amount)
        self.slippage = slippage
        self.amount_by_percent = 0
        self.gas_price = gas_price
        self.gas_limit = gas_limit
        self.multiplier_of_gas = multiplier_of_gas
        if amount_to:
            random_value = abs(random.uniform(amount_from, amount_to))
            self.amount = round(random_value, ndigits)
        if max_percent:
            random_percent = random.uniform(min_percent, max_percent) / 100
            self.amount_by_percent = round(random_percent, ndigits)
# endregion Class to get info about swap


# region Class to prepare data for swap/bridge/deposit/borrow etc.
class OperationProposal1(TypedDict):
    from_token: TokenContract | NativeTokenContract
    amount_from: TokenAmount
    to_token: TokenContract | NativeTokenContract
    min_amount_to: NotRequired[TokenAmount]
    

class InitOperationProposal:
    def __init__(
        self,
        from_token: TokenContract | NativeTokenContract,
        amount_from: TokenAmount,
        to_token: TokenContract | NativeTokenContract,
    ):
        self.from_token = from_token
        self.to_token = to_token
        self.amount_from = amount_from


class OperationProposal:
    def __init__(
        self,
        from_token: TokenContract | NativeTokenContract,
        amount_from: TokenAmount,
        to_token: TokenContract | NativeTokenContract,
        min_amount_to: TokenAmount
    ):
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
    """
    Derived classes should reassigned 
        PATHS: dict[str, dict[str: TxPayloadDetails]] = {}
    from TxPayloadDetailsFetcher to use it's methods
    """
    PATHS: dict[str, dict[str, TxPayloadDetails]] = {}

    @classmethod
    def get_tx_payload_details(
        cls,
        first_token: TokenSymbol,
        second_token: TokenSymbol
    ) -> TxPayloadDetails:
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
