from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


class GeneralDTO(BaseModel):
    id: int = Field(None)

    model_config = ConfigDict(from_attributes=True)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        """Return a string representation of the DTO instance.

        This representation includes the specified attributes in `repr_attrs`
        or the first `repr_attrs_num` attributes from the instance. It is designed
        to avoid loading relationships to prevent unexpected behavior.
        """
        attrs = []
        for idx, attr in enumerate(self.__dict__.keys()):
            if idx < 3:
                attrs.append(f'{attr}={getattr(self, attr)}')

        return f'{self.__class__.__name__}({", ".join(attrs)})'


class AccountDTO(GeneralDTO):
    account_name: Optional[str] = Field(None)
    evm_private_key: Optional[str] = Field(None)
    evm_address: Optional[str] = Field(None)
    next_action_time: Optional[datetime] = Field(None)
    planned_swaps_count: Optional[int] = Field(None)
    planned_mints_count: Optional[int] = Field(None)
    planned_bridges_count: Optional[int] = Field(None)
    planned_stakes_count: Optional[int] = Field(None)
    completed: Optional[bool] = Field(None)

    @field_validator('evm_private_key', mode='before')
    def check_evm_private_key(cls, v) -> str:
        if (
            isinstance(v, str)
            and v.startswith('0x')
            and len(v) == 66
        ):
            return v
        if (
            isinstance(v, str)
            and not v.startswith('0x')
            and len(v) == 64
        ):
            return '0x' + v
        raise ValueError('Invalid EVM private key')

    @field_validator('evm_address', mode='before')
    def check_evm_address(cls, v) -> str:
        if (
            isinstance(v, str)
            and v.startswith('0x')
            and len(v) == 42
        ):
            return v
        raise ValueError('Invalid EVM address')

    @field_validator('next_action_time', mode='before')
    def format_next_action_time(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return v  # Return as is if it's None or already a string

    class GetByEvmPrivateKey(GeneralDTO):
        evm_private_key: str

    class GetByEvmAddress(GeneralDTO):
        evm_address: str


class BridgeDTO(GeneralDTO):
    from_network: str = Field(None)
    to_network: str = Field(None)
    src_amount: Decimal | float | int = Field(None)
    src_token: str = Field(None)
    dst_amount: Decimal | float | int = Field(None)
    dst_token: str = Field(None)
    volume_usd: Decimal | float | int = Field(None)
    fee: Decimal | float | int = Field(None)
    fee_in_usd: float = Field(None)
    platform: str = Field(None)
    tx_hash: str = Field(None)
    account_id: int = Field(None)

    @field_validator('src_amount', 'dst_amount', 'volume_usd', 'fee', 'fee_in_usd', mode='before')
    def validate_amounts(cls, value):
        if isinstance(value, (float, int)):
            return round(float(value), 6)  # Round to 6 decimal places
        raise ValueError('Amount must be a float or int')

    @field_validator('from_network', 'to_network', 'src_token', 'dst_token', 'platform', 'tx_hash', mode='before')
    def validate_strings(cls, value):
        return str(value)


class MintDTO(GeneralDTO):
    nft: str = Field(None)
    nft_quantity_by_mint: int = Field(None)
    mint_price: Decimal | float | int = Field(None)
    mint_price_in_usd: float = Field(None)
    platform: str = Field(None)
    date: datetime = Field(None)
    tx_hash: str = Field(None)
    account_id: int = Field(None)


class SwapDTO(GeneralDTO):
    network: str = Field(None)
    src_amount: float = Field(None)
    src_token: str = Field(None)
    dst_amount: float = Field(None)
    dst_token: str = Field(None)
    volume_usd: float = Field(None)
    fee: float = Field(None)
    fee_in_usd: float = Field(None)
    platform: str = Field(None)
    tx_hash: str = Field(None)
    account_id: int = Field(None)


class StakeDTO(GeneralDTO):
    amount: float = Field(None)
    platform: str = Field(None)
    tx_hash: str = Field(None)
    account_id: int = Field(None)


# region Common filters
class GetByAccountId(GeneralDTO):
    account_id: int
# endregion
