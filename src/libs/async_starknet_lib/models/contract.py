from abc import ABC
from starknet_py.net.models import AddressRepresentation

from .common import AutoRepr
from ..data.config import DEFAULT_TOKEN_ABI_PATH


# region RawContract
class RawContract(AutoRepr):
    def __init__(
        self,
        title: str,
        address: AddressRepresentation,
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


# region TokenContractBase
class TokenContractBase(ABC, AutoRepr):
    """
    An abstract class of a token contract.
    """
    def __init__(
        self,
        title: str,
        address: AddressRepresentation,
        is_native_token: bool,
    ):
        self.title = title
        self.address = address
        self.is_native_token = is_native_token
# endregion TokenContractBase


# region TokenContract
class TokenContract(TokenContractBase):
    def __init__(
        self,
        title: str,
        address: AddressRepresentation,
        abi_or_path: list[str] | tuple[str] | str = DEFAULT_TOKEN_ABI_PATH,
        decimals: int | None = None,
    ) -> None:
        super().__init__(
            title=title,
            address=address,
            is_native_token=False
        )
        self.abi_path = abi_or_path
        self.decimals = decimals
# endregion TokenContract


# region NativeTokenContract
class NativeTokenContract(TokenContractBase):
    """
    An instance of a native token contract.
    """
    def __init__(
        self,
        title: str = 'ETH',
        address: AddressRepresentation = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
    ) -> None:
        """
        Initialize the NativeTokenContract.

        Args:
            title (str): The title or name of the native token.
            address (str): The address of the native token..
        """
        super().__init__(
            title=title,
            address=address,
            is_native_token=True
        )
# endregion NativeTokenContract
