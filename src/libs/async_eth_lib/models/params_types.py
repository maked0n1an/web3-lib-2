from web3.types import Address, ChecksumAddress
from web3.contract import AsyncContract, Contract
from .others import TokenAmount


Web3ContractType = AsyncContract | Contract
AddressType = str | Address | ChecksumAddress
AmountType = float | int | TokenAmount
GasPriceType = float | int | TokenAmount
GasLimitType = int | TokenAmount
