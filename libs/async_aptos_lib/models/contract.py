from aptos_sdk.account_address import AccountAddress

from .common import AutoRepr


#region RawAccount
class RawAccount(AutoRepr):
    def __init__(
        self,
        title: str,
        address: str | AccountAddress,
    ) -> None:
        """
        Initialize the class.

        Args:
            title (str): a account title.
            address (str): a account address.
        """
        self.title = title
        self.address = address
#endregion RawAccount


#region TokenAccount
class TokenAccount(RawAccount):
    def __init__(
        self, 
        title: str,
        address: str | AccountAddress,
        decimals: int | None = None,
        is_native_token: bool = False
    ) -> None:
        """
        Initialize the class.

        Args:
            title (str): a contract title.
            address (str): a account address.
            decimals (int): a account decimals.
            is_native_token (bool): is this account native token of network (False).
        """
        super().__init__(
            title = title,
            address=address,
        )
        self.decimals = decimals
        self.is_native_token = is_native_token
#endregion TokenAccount


#region NativeTokenAccount
class NativeTokenAccount(TokenAccount):
    def __init__(
        self,
        title: str,
        address: str | AccountAddress = '0x1::aptos_coin::AptosCoin',
        decimals: int = 8
    ) -> None:
        super().__init__(
            title=title,
            address=address,
            decimals=decimals,
            is_native_token=True
        )
#endregion NativeTokenAccount