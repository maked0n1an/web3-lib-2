from datetime import datetime
from typing import List

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    func,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    Mapped,
    mapped_column,
    relationship,
)

from .custom_types import (
    int_pk_an,
    str_66_unique_an,
    str_42_unique_an,
    str_30_an,
    str_10_an,
)

class BaseSqlModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int_pk_an]

    created_at: Mapped[datetime] = mapped_column(
        DATETIME(truncate_microseconds=True),
        server_default=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.split('Entity')[0].lower() + 's'

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        """Return a string representation of the model instance.

        This representation includes the specified columns in `repr_cols`
        or the first `repr_cols_num` columns from the table. It is designed
        to avoid loading relationships to prevent unexpected behavior.
        """
        """Relationship не используется в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f'{col}={getattr(self, col)}')

        return f'<{self.__class__.__name__}({" | ".join(cols)})>'


class AccountEntity(BaseSqlModel):
    id: Mapped[int_pk_an]
    account_name: Mapped[str_30_an | None]
    evm_private_key: Mapped[str_66_unique_an]
    evm_address: Mapped[str_42_unique_an]
    next_action_time: Mapped[datetime] = mapped_column(DATETIME(truncate_microseconds=True))
    planned_swaps_count: Mapped[int]
    planned_mints_count: Mapped[int]
    planned_bridges_count: Mapped[int]
    planned_stakes_count: Mapped[int]
    completed: Mapped[bool] = mapped_column(default=False, server_default='0')
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME(truncate_microseconds=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        Index("evm_pk", "evm_private_key"),
    )
    bridges: Mapped[List['BridgeEntity']] = relationship(
        back_populates='account',
        cascade='all, delete-orphan'
    )
    mints: Mapped[List['MintEntity']] = relationship(
        back_populates='account',
        cascade="all, delete-orphan"
    )
    stakes: Mapped[List["StakeEntity"]] = relationship(
        back_populates='account',
        cascade="all, delete-orphan"
    )
    swaps: Mapped[List['SwapEntity']] = relationship(
        back_populates='account',
        cascade="all, delete-orphan"
    )


class BridgeEntity(BaseSqlModel):
    id: Mapped[int_pk_an]
    from_network: Mapped[str_30_an]
    to_network: Mapped[str_30_an]
    src_amount: Mapped[float]
    src_token: Mapped[str_10_an]
    dst_amount: Mapped[float]
    dst_token: Mapped[str_10_an]
    volume_usd: Mapped[float]
    fee: Mapped[float]
    fee_in_usd: Mapped[float]
    platform: Mapped[str_30_an]
    tx_hash: Mapped[str]

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounts.id', ondelete="CASCADE")
    )
    account: Mapped['AccountEntity'] = relationship(back_populates='bridges')


class MintEntity(BaseSqlModel):
    id: Mapped[int_pk_an]
    nft: Mapped[str]
    nft_quantity_by_mint: Mapped[int]
    mint_price: Mapped[float]
    mint_price_in_usd: Mapped[float]
    platform: Mapped[str_30_an]
    tx_hash: Mapped[str]

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounts.id', ondelete="CASCADE")
    )
    account: Mapped['AccountEntity'] = relationship(back_populates='mints')


class StakeEntity(BaseSqlModel):
    id: Mapped[int_pk_an]
    token: Mapped[str_10_an]
    amount: Mapped[float]
    unfreeze_date: Mapped[datetime | None]
    platform: Mapped[str_30_an]
    tx_hash: Mapped[str]

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounts.id', ondelete="CASCADE")
    )
    account: Mapped['AccountEntity'] = relationship(back_populates='stakes')


class SwapEntity(BaseSqlModel):
    id: Mapped[int_pk_an]
    network: Mapped[str_30_an]
    src_amount: Mapped[float]
    src_token: Mapped[str_10_an]
    dst_amount: Mapped[float]
    dst_token: Mapped[str_10_an]
    volume_usd: Mapped[float]
    fee: Mapped[float]
    fee_in_usd: Mapped[float]
    platform: Mapped[str_30_an]
    tx_hash: Mapped[str]

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounts.id', ondelete="CASCADE")
    )
    account: Mapped['AccountEntity'] = relationship(back_populates='swaps')
