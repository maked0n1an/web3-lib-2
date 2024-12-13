from web3 import Web3
from web3.types import (
    Address,
    ChecksumAddress,
)

from libs.async_eth_lib.models.dataclasses import DefaultAbis

from .common import AutoRepr


# region RawContract
class RawContract(AutoRepr):
    def __init__(
        self,
        title: str,
        address: str | Address | ChecksumAddress,
        abi_path: list[str] | tuple[str] | str
    ):
        """
        Initialize the class.

        Args:
            title (str): a contract title.
            address (str): a contract address.
            abi_path (tuple | list | str]): a path to get contract ABI from file.
        """
        self.title = title
        self.address = Web3.to_checksum_address(address)
        self.abi_path = abi_path
# endregion RawContract


# region TokenContract
class TokenContract(RawContract):
    def __init__(
        self,
        title: str,
        address: str | Address | ChecksumAddress,
        abi_path: list[str] | tuple[str] | str = DefaultAbis.ERC_20,
        decimals: int | None = None,
    ):
        """
        Initialize the class.

        Args:
            title (str): a contract title.
            address (str): a contract address.
            abi_path (tuple | list | str): a path to get contract ABI from file.
            decimals (int): a contract decimals.
            is_native_token (bool): is this contract native token of network (False).
        """
        super().__init__(
            title=title,
            address=address,
            abi_path=abi_path
        )
        self.decimals = decimals
        self.is_native_token = False
# endregion TokenContract


# region NativeTokenContract
class NativeTokenContract(AutoRepr):
    """
    An instance of a native token contract.

    Attributes:
        title (str): The title or name of the native token.
    """

    def __init__(
        self,
        title: str = 'ETH',
        address: str | Address | ChecksumAddress = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
    ):
        """
        Initialize the NativeTokenContract.

        Args:
            title (str): The title or name of the native token.

        """
        self.title = title
        self.address = Web3.to_checksum_address(address)
        self.decimals = 18
        self.is_native_token = True
# endregion NativeTokenContract
