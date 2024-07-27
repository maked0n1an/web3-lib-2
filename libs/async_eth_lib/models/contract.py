import json

from web3 import (
    Web3,
    types
)
from typing import Any
from eth_typing import ChecksumAddress

from libs.async_eth_lib.models.dataclasses import DefaultAbis
from libs.pretty_utils.type_functions.classes import AutoRepr


#region RawContract
class RawContract(AutoRepr):
    def __init__(
        self,
        title: str,
        address: str | types.Address | types.ChecksumAddress | types.ENS,
        abi_path: list[str] | tuple[str] | str | None
    ) -> None:
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
#endregion RawContract


#region TokenContract
class TokenContract(RawContract):
    def __init__(
        self, 
        title: str,
        address: str | types.Address | types.ChecksumAddress | types.ENS, 
        abi_path: list[str] | tuple[str] | str = None,
        decimals: int | None = None,
        is_native_token: bool = False
    ) -> None:
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
            title = title,
            address=address,
            abi_path=abi_path
        )
        self.decimals = decimals
        self.is_native_token = is_native_token
#endregion TokenContract


#region NativeTokenContract
class NativeTokenContract(TokenContract):
    """
    An instance of a native token contract.

    Attributes:
        title (str): The title or name of the native token.

    """

    def __init__(
        self,
        title: str,
        address: str = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
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
#endregion NativeTokenContract