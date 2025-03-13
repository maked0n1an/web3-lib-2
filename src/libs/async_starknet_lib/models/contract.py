from abc import ABC
from src.libs.async_eth_lib.models.type_alias import AbiType
from starknet_py.net.models import AddressRepresentation

from .common import AutoRepr
from ..data.config import DEFAULT_TOKEN_ABI_PATH


class BaseContract(AutoRepr):
    @property
    def title(self) -> str:
        return self.__title

    @property
    def address(self) -> AddressRepresentation:
        return self.__address

    def __init__(
        self,
        title: str,
        address: AddressRepresentation,
    ):
        self.__title = title
        self.__address = address


# region RawContract
class RawContract(BaseContract):
    """
    An instance of a raw contract.
    """
    @property
    def abi_or_path(self) -> AbiType:
        return self.__abi_or_path

    def __init__(
        self,
        title: str,
        address: AddressRepresentation,
        abi_or_path: AbiType
    ):
        """
        Initialize the class.

        Args:
            title (str): a contract title.
            address (str): a contract address.
            abi_path (tuple | list | str]): a path to get contract ABI from file.
        """
        super().__init__(
            title=title,
            address=address
        )
        self.__abi_or_path = abi_or_path
# endregion RawContract


# region TokenContract
class TokenContract(RawContract):
    """
    An instance of a ERC_20 token contract.
    """
    @property
    def is_native_token(self) -> bool:
        return self.__is_native_token

    def __init__(
        self,
        title: str,
        address: AddressRepresentation,
        abi_or_path: AbiType = DEFAULT_TOKEN_ABI_PATH,
        decimals: int | None = None,
    ):
        """
        Initialize the TokenContract class.

        Args:
            title (str): a contract title.
            address (str | Address | ChecksumAddress): a contract address.
            abi_or_path (str | list[str] | tuple[str] | dict | list[dict]): a path to get contract ABI from file (default is ERC_20 abi).
            decimals (int): a contract decimals (default is None).
        """
        super().__init__(
            title=title,
            address=address,
            abi_or_path=abi_or_path
        )
        self.__is_native_token = False
        
        self.decimals = decimals
# endregion TokenContract


# region NativeTokenContract
class NativeTokenContract(BaseContract):
    """
    An instance of a native token contract.
    """
    @property
    def is_native_token(self) -> bool:
        return self.__is_native_token

    def __init__(
        self,
        title: str = 'ETH',
        address: AddressRepresentation = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
    ):
        """
        Initialize the NativeTokenContract.

        Args:
            title (str): The title or name of the native token.
            address (str): The address of the native token.
        """
        super().__init__(
            title=title,
            address=address
        )
        self.__is_native_token = True
# endregion NativeTokenContract
