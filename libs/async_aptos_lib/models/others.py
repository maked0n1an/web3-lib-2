from decimal import Decimal


# region Constants
class TokenSymbol:
    APT     = 'APT'
    
    ETH     = 'ETH'
    USDT    = 'USDT'
    DAI     = 'DAI'
    USDC    = 'USDC'
    WBTC    = 'WBTC'
    WETH    = 'WETH'
    
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
    DEPOSITED = 'DEPOSITED'
    WITHDRAWN = 'WITHDRAWN'
# endregion Constants


# region TokenAmount
class TokenAmount:
    """
    A class representing a token amount.

    Attributes:
        Octa (int): The amount in Octas.
        Ether (Decimal): The amount in Ether.
        decimals (int): The number of decimal places.
    """
    def __init__(
        self,
        amount: int | float | Decimal | str,
        decimals: int = 8,
        is_octas: bool = False,
    ) -> None:
        """
        Initialize the TokenAmount class.

        Args:
            amount (int | float | Decimal | str): The amount.
            decimals (int): The number of decimal places (default is 18).
            is_octas (bool): If True, the amount is in Octas; otherwise, it's in Aptos (default is False).
        """
        if is_octas:
            self.Octa: int = int(amount)
            self.Aptos: Decimal = Decimal(str(amount)) / 10 ** decimals

        else:
            self.Octa: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Aptos: Decimal = Decimal(str(amount))

        self.decimals = decimals

    def __str__(self) -> str:
        """
        Return a string representation of the TokenAmount.

        Returns:
            str: A string representation of the TokenAmount.

        """
        return str(self.Aptos)
