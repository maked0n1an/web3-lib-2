from datetime import datetime
from typing import Annotated, List

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    Mapped,
    mapped_column,
    relationship
)
from sqlalchemy.ext.asyncio import AsyncAttrs


int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
str_66 = Annotated[str, 66, mapped_column(unique=True)]
str_42 = Annotated[str, 42, mapped_column(unique=True)]
created_at = Annotated[datetime, mapped_column(
    server_default=func.now())]


class SqlBaseModel(AsyncAttrs, DeclarativeBase):
    id = None

    type_annotation_map = {
        str_66: String(66),
        str_42: String(42),
    }

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.split('ORM')[0].lower() + 's'

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

        return f'<{self.__class__.__name__} {"| ".join(cols)}>'


class AccountORM(SqlBaseModel):
    id: Mapped[int_pk]
    account_name: Mapped[Annotated[str, mapped_column(String(30), nullable=True)]]
    evm_private_key: Mapped[str_66]
    evm_address: Mapped[str_42]
    next_action_time: Mapped[datetime | None]
    planned_swaps_count: Mapped[int]
    planned_mint_count: Mapped[int]
    planned_lending_count: Mapped[int]
    planned_stake_count: Mapped[int]
    completed: Mapped[bool] = mapped_column(default=False, server_default='0')

    __table_args__ = (
        Index("evm_pk", "evm_private_key"),
    )

    swaps: Mapped[List['SwapORM']] = relationship(
        back_populates='account',
        cascade="all, delete-orphan"
    )
    mints: Mapped[List['MintORM']] = relationship(
        back_populates='account',
        cascade="all, delete-orphan"
    )
    lendings: Mapped[List["LendingORM"]] = relationship(
        back_populates='account',
        cascade="all, delete-orphan"
    )
    stakes: Mapped[List["StakeORM"]] = relationship(
        back_populates='account',
        cascade="all, delete-orphan"
    )


class MintORM(SqlBaseModel):
    id: Mapped[int_pk]
    nft_name: Mapped[str]
    nft_market_name: Mapped[str]
    nft_quantity_by_mint: Mapped[str]
    mint_price: Mapped[float]
    mint_price_in_usd: Mapped[float]
    date: Mapped[created_at]
    tx_hash: Mapped[str]

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounts.id', ondelete="CASCADE")
    )
    account: Mapped['AccountORM'] = relationship(back_populates='mints')


class StakeORM(SqlBaseModel):
    id: Mapped[int_pk]
    platform: Mapped[str]
    amount: Mapped[float]
    currency: Mapped[str]
    reward_rate: Mapped[float]
    unfreeze_date: Mapped[datetime | None]
    date: Mapped[created_at]
    tx_hash: Mapped[str]

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounts.id', ondelete="CASCADE")
    )
    account: Mapped['AccountORM'] = relationship(back_populates='stakes')


class SwapORM(SqlBaseModel):
    id: Mapped[int_pk]
    trade_pair: Mapped[str]
    dex_name: Mapped[str]
    volume: Mapped[float]
    volume_usd: Mapped[float]
    fee: Mapped[float]
    date: Mapped[created_at]
    tx_hash: Mapped[str]

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounts.id', ondelete="CASCADE")
    )
    account: Mapped['AccountORM'] = relationship(back_populates='swaps')


class LendingORM(SqlBaseModel):
    id: Mapped[int_pk]
    platform: Mapped[str]
    amount: Mapped[float]
    currency: Mapped[str]
    fee: Mapped[float]
    date: Mapped[created_at]
    tx_hash: Mapped[str]

    account_id: Mapped[int] = mapped_column(
        ForeignKey('accounts.id', ondelete="CASCADE")
    )
    account: Mapped['AccountORM'] = relationship(back_populates='lendings')
