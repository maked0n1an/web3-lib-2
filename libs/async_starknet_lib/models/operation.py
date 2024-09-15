import random

from .contract import TokenContract
from .others import TokenAmount


# region Class to get info about swap
class OperationInfo:
    def __init__(
        self,
        from_token_name: str = None,
        to_token_name: str = None,
        slippage: float = 0.5,
        amount: float | None = None,
        amount_from: float | None = None,
        amount_to: float | None = None,
        ndigits: int = 5,
        min_percent: int | None = None,
        max_percent: int | None = None,
        gas_price: float | None = None,
        gas_limit: int | None = None,
        multiplier_of_gas: float | None = None
    ) -> None:
        """
        Initialize the SwapInfo class.

        Args:
            from_token_name (str): The token to swap from.
            to_token_name (str): The token to swap to.
            slippage (float): The slippage tolerance (default is 0.5).
            src_network_name (str | None): The source network for the swap (default is None).
            dst_network_name (str | None): The destination network for the swap (default is None).
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
        self.amount = amount
        self.slippage = slippage
        self.amount_by_percent = 0
        self.gas_price = gas_price
        self.gas_limit = gas_limit
        self.multiplier_of_gas = multiplier_of_gas
        if amount_from and amount_to:
            self.amount = self._get_random_amount(
                amount_from, amount_to, ndigits)
        if min_percent and max_percent:
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


# region Class to prepare swap
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