from starknet_py.net.models import Address

from .common import AutoRepr


# region RawContract
class RawContract(AutoRepr):
    def __init__(
        self,
        title: str,
        address: Address,
        abi_path: list[str] | tuple[str] | str | None
    ) -> None:
        """
        Initialize the class.

        Args:
            title (str): a contract title.
            address (str): a contract address.
            abi (Union[List[Dict[str, Any]], str]): an ABI of the contract.
            is_native_token (bool): is this contract native token of network (False)
        """
        self.title = title
        self.address = address
        self.abi_path = abi_path
# endregion RawContract


# region TokenContract
class TokenContract(RawContract):
    def __init__(
        self,
        title: str,
        address: Address,
        abi_path: list[str] | tuple[str] | str = None,
        decimals: int | None = None,
        is_native_token: bool = False
    ) -> None:
        super().__init__(
            title=title,
            address=address,
            abi_path=abi_path
        )
        self.decimals = decimals
        self.is_native_token = is_native_token
# endregion TokenContract


# region NativeTokenContract
class NativeTokenContract(TokenContract):
    """
    An instance of a native token contract.

    Attributes:
        title (str): The title or name of the native token.

    """

    def __init__(
        self,
        title: str,
        address: Address = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
        abi_path: list[str] | tuple[str] | str = None,
        decimals: int = 18
    ) -> None:
        """
        Initialize the NativeTokenContract.

        Args:
            title (str): The title or name of the native token.

        """
        super().__init__(
            title=title,
            address=address,
            abi_path=abi_path,
            decimals=decimals,
            is_native_token=True
        )
# endregion NativeTokenContract
