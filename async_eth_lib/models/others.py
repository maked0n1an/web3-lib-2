from decimal import Decimal
from web3 import types
from web3.contract import AsyncContract, Contract

from async_eth_lib.models.contract import (
    NativeTokenContract,
    RawContract,
    TokenContract
)

# region Common
class Autorepr:
    """Contains a __repr__ function that automatically builds the output of a class using all its variables."""

    def __repr__(self) -> str:
        values = ('{}={!r}'.format(key, value)
                  for key, value in vars(self).items())
        return '{}({})'.format(self.__class__.__name__, ', '.join(values))


class Singleton(type):
    """A class that implements the singleton pattern."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(cls, *args, **kwargs)
        return cls._instances[cls]
# endregion Common


# region Constants
class TokenSymbol:
    ETH = 'ETH'

    ARB = 'ARB'
    AVAX = 'AVAX'
    BNB = 'BNB'
    BUSD = 'BUSD'
    CELO = 'CELO'
    CORE = 'CORE'
    DAI = 'DAI'
    FRAX = 'FRAX'
    FTM = 'FTM'
    GETH = 'GETH'
    GETH_LZ = 'GETH_LZ'
    GLMR = 'GLMR'
    HECO = 'HECO'
    KAVA = 'KAVA'
    MATIC = 'MATIC'
    STG = 'STG'
    USDT = 'USDT'
    USDC = 'USDC'
    USDC_E = 'USDC_E'
    USDV = 'USDV'
    WBTC = 'WBTC'
    WETH = 'WETH'
    XDAI = 'xDAI'


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
# endregion Constants


# region TokenAmount
class TokenAmount:
    """
    A class representing a token amount.

    Attributes:
        Wei (int): The amount in Wei.
        Ether (Decimal): The amount in Ether.
        decimals (int): The number of decimal places.
        GWei (int): The amount in Gwei.

    """
    Wei: int
    Ether: Decimal
    decimals: int
    GWei: int

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
                self.GWei: Decimal = int(amount / 10 ** 9)
        else:
            self.Wei: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether: Decimal = Decimal(str(amount))

            if set_gwei:
                self.GWei: Decimal = int(Decimal(str(amount)) * 10 ** 9)

        self.decimals = decimals

    def __str__(self) -> str:
        """
        Return a string representation of the TokenAmount.

        Returns:
            str: A string representation of the TokenAmount.

        """
        return str(self.Wei)


#region Params types
ContractUnion = RawContract | AsyncContract | Contract
TokenContractUnion = TokenContract | NativeTokenContract
AddressUnion = str | types.Address | types.ChecksumAddress | types.ENS
AmountUnion = float | int | TokenAmount
GasPriceUnion = float | int | TokenAmount
GasLimitUnion = int | TokenAmount
#endregion Params types