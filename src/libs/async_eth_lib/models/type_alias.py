from typing import TypeAlias

from eth_typing.evm import Address, ChecksumAddress

from .others import TokenAmount


AbiType: TypeAlias = str | list[str] | dict | list[dict]
AddressType: TypeAlias = str | Address | ChecksumAddress
AmountType: TypeAlias = float | int | TokenAmount
GasLimitType: TypeAlias = int | TokenAmount
GasPriceType: TypeAlias = float | int | TokenAmount
