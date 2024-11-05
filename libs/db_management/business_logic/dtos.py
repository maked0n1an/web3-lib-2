from dataclasses import dataclass
from pydantic import (
    BaseModel, ConfigDict, field_validator, ValidationError
)
from datetime import datetime
from decimal import Decimal

from ..data_access.entities import AccountEntity
from ..data_access.repository._generic import TEntity


class TxHashValidator:
    @field_validator('platform', mode='before')
    def validate_platform(cls, v) -> str:
        if isinstance(v, str):
            return v
        raise ValueError('Platform must be a string')

    @field_validator('tx_hash', mode='before')
    def validate_tx_hash(cls, v) -> str:
        if isinstance(v, str) and v.startswith('0x'):
            return v
        raise ValueError('Tx hash must be a hex string')


class ExchangeValidator(TxHashValidator):
    @field_validator('src_amount', mode='before')
    def round_src_amount(cls, v) -> float:
        if isinstance(v, (Decimal, float, int)):
            return round(float(v), 6)
        raise ValueError('Amount must be a number')

    @field_validator('dst_amount', mode='before')
    def round_dst_amount(cls, v) -> float:
        if isinstance(v, (Decimal, float, int)):
            return round(float(v), 6)
        raise ValueError('Amount must be a number')

    @field_validator('volume_usd', mode='before')
    def round_volume_usd(cls, v) -> float:
        if isinstance(v, (Decimal, float, int)):
            return round(float(v), 3)
        raise ValueError('Volume usd must be a number')

    @field_validator('fee', mode='before')
    def round_fee(cls, v) -> float:
        if isinstance(v, (Decimal, float, int)):
            return round(float(v), 6)
        raise ValueError('Fee must be a number')

    @field_validator('fee_in_usd', mode='before')
    def round_fee_in_usd(cls, v) -> float:
        if isinstance(v, (Decimal, float, int)):
            return round(float(v), 3)
        raise ValueError('Fee in usd must be a number')


class GeneralDTO:
    # model_config = ConfigDict(from_attributes=True)

    # @classmethod
    # def validate_back(
    #     cls,
    #     entity_type: type[TEntity]
    # ) -> TEntity:
    #     try:
    #         dto_data = cls.model_dump()
    #         entity = entity_type(**dto_data)
    #         return entity
    #     except ValidationError as e:
    #         raise ValueError(f'Invalid data: {e}')

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
    id: int
    account_name: str | None
    evm_private_key: str
    evm_address: str
    next_action_time: datetime | None
    planned_swaps_count: int
    planned_mint_count: int
    planned_lending_count: int
    planned_stake_count: int
    completed: bool

    # def __init__(
    #     self,
    #     id: int = 0,
    #     account_name: str = '',
    #     evm_address: str = '',
    #     evm_private_key: str = '',
    #     next_action_time: datetime | None = datetime.now(),
    #     planned_swaps_count: int = 0,
    #     planned_mint_count: int = 0,
    #     planned_lending_count: int = 0,
    #     planned_stake_count: int = 0,
    #     completed: bool = False
    # ):
    #     self.id = id
    #     self.account_name = str(account_name)
    #     self.evm_address = str(evm_address)
    #     self.evm_private_key = str(evm_private_key)
    #     self.next_action_time = next_action_time
    #     self.planned_swaps_count = planned_swaps_count
    #     self.planned_mint_count = planned_mint_count
    #     self.planned_lending_count = planned_lending_count
    #     self.planned_stake_count = planned_stake_count
    #     self.completed = completed


class BridgeDTO(
    GeneralDTO, 
    # ExchangeValidator
):
    id: int
    from_network: str
    to_network: str
    src_amount: Decimal | float | int
    src_token: str
    dst_amount: Decimal | float | int
    dst_token: str
    volume_usd: Decimal | float | int
    fee: Decimal | float | int
    fee_in_usd: float
    platform: str
    tx_hash: str
    account_id: int

    def __init__(
        self,
        account_id: int = 0,
        from_network: str = '',
        to_network: str = '',
        src_amount: float = 0.0,
        src_token: str = '',
        dst_amount: float = 0.0,
        dst_token: str = '',
        volume_usd: Decimal | float | int = 0.0,
        fee: Decimal | float | int = 0.0,
        fee_in_usd: float = 0.0,
        platform: str = '',
        tx_hash: str = ''
    ):
        self.from_network = str(from_network)
        self.to_network = str(to_network)
        self.src_amount = round(float(src_amount), 6)
        self.src_token = str(src_token)
        self.dst_amount = round(float(dst_amount), 6)
        self.dst_token = str(dst_token)
        self.volume_usd = round(float(volume_usd), 6)
        self.fee = round(float(fee), 6)
        self.fee_in_usd = round(fee_in_usd, 2)
        self.platform = str(platform)
        self.tx_hash = str(tx_hash)
        self.account_id = int(account_id)

    # @field_validator('from_network', mode='before')
    # def validate_from_network(cls, v) -> str:
    #     if isinstance(v, str):
    #         return v
    #     raise ValueError('Src network must be a string')

    # @field_validator('to_network', mode='before')
    # def validate_to_network(cls, v) -> str:
    #     if isinstance(v, str):
    #         return v
    #     raise ValueError('Dst network must be a string')


class MintDTO(GeneralDTO, TxHashValidator):
    id: int
    nft: str
    nft_quantity_by_mint: int
    mint_price: Decimal | float | int
    mint_price_in_usd: float
    platform: str
    date: datetime
    tx_hash: str
    account_id: int


class SwapDTO(GeneralDTO, TxHashValidator):
    id: int
    network: str
    src_amount: float
    src_token: str
    dst_amount: float
    dst_token: str
    volume_usd: float
    fee: float
    fee_in_usd: float
    platform: str
    tx_hash: str

    @field_validator('network', mode='before')
    def validate_network(cls, v) -> str:
        if isinstance(v, str):
            return v
        raise ValueError('Network must be a string')
