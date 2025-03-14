from decimal import Decimal


# region Constants
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
    """
    def __init__(
        self,
        amount: int | float | Decimal | str,
        decimals: int = 18,
        wei: bool = False,
        set_gwei: bool = False
    ) -> None:
        """
        Initialize the TokenAmount class.

        Args:
            amount (int | float | Decimal | str): The amount.
            decimals (int): The number of decimal places (default is 18).
            wei (bool): If True, the amount is in Wei; otherwise, it's in Ether (default is False).
            set_gwei (bool): If True, the GWei attribute will be calculated and set (default is False).

        """
        if wei:
            self.Wei: int = int(amount)
            self.Ether: Decimal = Decimal(str(amount)) / 10 ** decimals

            if set_gwei:
                self.GWei: int = int(Decimal(str(amount)) / 10 ** 9)
        else:
            self.Wei: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether: Decimal = Decimal(str(amount))

            if set_gwei:
                self.GWei: int = int(Decimal(str(amount)) * 10 ** 9)

        self.decimals = decimals

    def __str__(self) -> str:
        """
        Return a string representation of the TokenAmount.

        Returns:
            str: A string representation of the TokenAmount.

        """
        return str(self.Ether)


# region Others
class WalletType:
    ARGENT = 'Argent X'
    BRAAVOS = 'Braavos'


class StarkAccount:
    def __init__(
        self, 
        mnemonic, 
        private_key = '', 
        address = '',
        wallet_type = ''
    ):
        self.mnemonic = mnemonic
        self.private_key = private_key
        self.address = address
        self.wallet_type = wallet_type

    def to_list(self):
        return [self.address, self.private_key, self.mnemonic, self.wallet_type]
