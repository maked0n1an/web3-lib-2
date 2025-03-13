from typing import TypeAlias, Union

from .contract import TokenContract, NativeTokenContract


TokenContractType: TypeAlias = Union[TokenContract, NativeTokenContract]
