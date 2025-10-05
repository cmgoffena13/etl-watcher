from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import Column, Index, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel


class AddressType(SQLModel, table=True):
    __tablename__ = "address_type"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(max_length=150, min_length=1)
    group_name: str = Field(max_length=150, min_length=1)

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

    __table_args__ = (
        Index(
            "ux_address_type_name_include",
            "name",
            unique=True,
            postgresql_include=["id"],
        ),
    )
