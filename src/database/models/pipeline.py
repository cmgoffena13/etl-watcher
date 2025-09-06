from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Column, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel


class Pipeline(SQLModel, table=True):
    __tablename__ = "pipeline"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(
        index=True, unique=True, nullable=False, max_length=150, min_length=1
    )
    pipeline_type_id: int = Field(foreign_key="pipeline_type.id", nullable=False)
    created_at: DateTime = Field(
        sa_column=Column(
            DateTimeTZ(timezone=True),
            nullable=False,
            server_default=text(
                "CURRENT_TIMESTAMP"
            ),  # Have Postgres generate the timestamp
        ),
    )
    updated_at: Optional[DateTime] = Field(
        sa_column=Column(DateTimeTZ(timezone=True), nullable=True)
    )
