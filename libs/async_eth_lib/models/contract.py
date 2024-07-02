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
    """
    An instance of a raw contract.

    Attributes:
        title (str): a contract title.
        address (ChecksumAddress): a contract address.
        abi (list[dict[str, Any]] | str): an ABI of the contract.
        is_native_token (bool): is this contract native token of network (False)

    """
    title: str
    address: ChecksumAddress
    abi: list[dict[str, Any]]
    
    def __init__(
        self,
        title: str,
        address: str | types.Address | types.ChecksumAddress | types.ENS,
        abi: list[dict[str, any]] | str
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
        self.address = Web3.to_checksum_address(address)
        self.abi = json.loads(abi) if isinstance(abi, str) else abi
#endregion RawContract


#region TokenContract
class TokenContract(RawContract):
    def __init__(
        self, 
        title: str,
        address: str | types.Address | types.ChecksumAddress | types.ENS, 
        abi: list[dict[str, Any]] | str = DefaultAbis.Token,
        decimals: int | None = None,
        is_native_token: bool = False
    ) -> None:
        super().__init__(
            title = title,
            address=address,
            abi=abi
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
        abi: list[dict[str, Any]] | str = DefaultAbis.Token,
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
            abi=abi,
            decimals=decimals,
            is_native_token=True
        )
#endregion NativeTokenContract