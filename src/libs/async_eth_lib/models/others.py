from decimal import Decimal
from web3.types import Wei


class LogStatus:
    DELAY = 'DELAY'
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

    FAILED = 'FAILED'
    APPROVED = 'APPROVED'
    MINTED = 'MINTED'
    BRIDGED = 'BRIDGED'
    SWAPPED = 'SWAPPED'


# region TokenAmount
class TokenAmount:
    """
    A class representing a token amount.

    """
    def __init__(
        self,
        amount: int | float | Decimal | str,
        decimals: int = 18,
        is_wei: bool = False,
        set_gwei: bool = False
    ) -> None:
        """
        Initialize the TokenAmount class.

        Args:
            amount (int | float | Decimal | str): The amount.
            decimals (int): The number of decimal places (default is 18).
            is_wei (bool): If True, the amount is in Wei; otherwise, it's in Ether (default is False).
            set_gwei (bool): If True, the GWei attribute will be calculated and set (default is False).

        """
        if is_wei:
            wei = Wei(int(amount))
            ether = Decimal(str(amount)) / 10 ** decimals

            if set_gwei:
                gwei = int(Decimal(str(amount)) / 10 ** 9)
        else:
            wei = Wei(int(Decimal(str(amount)) * 10 ** decimals))
            ether = Decimal(str(amount)) / 10 ** decimals

            if set_gwei:
                gwei = int(Decimal(str(amount)) * 10 ** 9)

        self.Wei: Wei = wei
        self.Ether: Decimal = ether
        self.GWei: int = gwei
        self.decimals = decimals

    def __str__(self) -> str:
        return str(self.Ether)
