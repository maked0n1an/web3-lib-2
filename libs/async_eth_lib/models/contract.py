from abc import ABC
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


# region TokenContractBase
class TokenContractBase(ABC, AutoRepr):
    """
    An abstract class of a token contract.
    """
    def __init__(
        self,
        title: str,
        address: str | Address | ChecksumAddress,
        is_native_token: bool,
    ):
        self.title = title
        self.address = Web3.to_checksum_address(address)
        self.is_native_token = is_native_token
# endregion TokenContractBase


# region TokenContract
class TokenContract(TokenContractBase):
    """
    An instance of a ERC_20 token contract.
    """
    def __init__(
        self,
        title: str,
        address: str | Address | ChecksumAddress,
        abi_or_path: list[str] | tuple[str] | str = DefaultAbis.ERC_20,
        decimals: int | None = None,
    ):
        """
        Initialize the TokenContract class.

        Args:
            title (str): a contract title.
            address (str | Address | ChecksumAddress): a contract address.
            abi_path (list[str] | tuple[str] | str): a path to get contract ABI from file (default is ERC_20 abi).
            decimals (int): a contract decimals.
        """
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
        address: str | Address | ChecksumAddress = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
    ):
        """
        Initialize the NativeTokenContract.

        Args:
            title (str): The title or name of the native token.
            address (str): The address of the native token.
        """
        super().__init__(
            title=title,
            address=address,
            is_native_token=True
        )
# endregion NativeTokenContract
