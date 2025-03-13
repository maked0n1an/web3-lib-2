from web3 import Web3
from eth_typing import (
    Address,
    ChecksumAddress,
)

from src._types.tokens import TokenSymbol

from .common import AutoRepr
from .type_alias import AbiType, AddressType
from ..models.dataclasses import DefaultAbis


class BaseContract(AutoRepr):
    @property
    def title(self) -> str:
        return self.__title

    @property
    def address(self) -> ChecksumAddress:
        return self.__address

    def __init__(
        self,
        title: str,
        address: str | Address | ChecksumAddress,
    ):
        self.__title = title
        self.__address = Web3.to_checksum_address(address)


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
        address: AddressType,
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
        title: TokenSymbol,
        address: AddressType,
        abi_or_path: AbiType = DefaultAbis.ERC_20,
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
        title: TokenSymbol = TokenSymbol.ETH,
        address: AddressType = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
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
