import datetime
import enum
from typing import List, Annotated

from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)

intpk = Annotated[int, mapped_column(primary_key=True)]
str_256 = Annotated[str, 256]
created_at = Annotated[datetime.datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"),
    onupdate=datetime.datetime.utcnow,
)]


class SqlBaseModel(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256)
    }

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

        return f'<{self.__class__.__name__} {', '.join(cols)}>'


class WorkLoad(enum.Enum):
    parttime = 'parttime'
    fulltime = 'fulltime'


class WorkersOrm(SqlBaseModel):
    __tablename__ = 'workers'

    id: Mapped[intpk]
    username: Mapped[str]
    
    resumes: Mapped[List['ResumesOrm']] = relationship(
        back_populates='worker'
    )
    resumes_parttime: Mapped[List['ResumesOrm']] = relationship(
        back_populates='worker',
        # primaryjoin="and_(WorkerOrm.id == ResumesOrm.worker_id, ResumesOrm.workload == 'parttime')",
        # order_by="ResumesOrm.id.desc()",
    ) 


class ResumesOrm(SqlBaseModel):
    __tablename__ = 'resumes'

    id: Mapped[intpk]
    title: Mapped[str_256]
    compensation: Mapped[int | None]
    workload: Mapped[WorkLoad]
    worker_id: Mapped[int] = mapped_column(ForeignKey('workers.id', ondelete="CASCADE"))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    worker: Mapped['WorkersOrm'] = relationship(
        back_populates='resumes'
    )
    
    __table_args__ = (
        Index("title_index", "title"),
        CheckConstraint("compensation > 0", name="check_compensation_positive")
    )
