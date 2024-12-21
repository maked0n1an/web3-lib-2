import random

from .contract import TokenContractBase
from .others import TokenAmount


# region Class to get info about swap
class OperationInfo:
    def __init__(
        self,
        from_token_name: str = None,
        to_token_name: str = None,
        slippage: float = 0.5,
        amount: float = 0,
        amount_from: float = 0,
        amount_to: float = None,
        ndigits: int = 5,
        min_percent: int = 0,
        max_percent: int = 100,
        gas_price: float = None,
        gas_limit: int = None,
        multiplier_of_gas: float = None
    ) -> None:
        """
        Initialize the OperationInfo class.

        Args:
            from_token_name (str): The name of the token to swap from.
            to_token_name (str): The name of the token to swap to.
            slippage (float): The slippage percentage for the swap.
            amount (float): The amount of the token to swap.
            amount_from (float): The minimum amount for random generation.
            amount_to (float): The maximum amount for random generation.
            ndigits (int): The number of decimal places for rounding.
            min_percent (int): The minimum percentage for random generation.
            max_percent (int): The maximum percentage for random generation.
            gas_price (float | None): The gas price for the transaction.
            gas_limit (int | None): The gas limit for the transaction.
            multiplier_of_gas (float | None): The multiplier for gas calculation.
        
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
        random_value = abs(random.uniform(amount_from, amount_to))
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
        from_token: TokenContractBase,
        amount_from: TokenAmount,
        to_token: TokenContractBase,
        min_amount_to: TokenAmount
    ) -> None:
        """
        Initialize the OperationProposal class.

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