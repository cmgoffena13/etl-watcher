from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlalchemy import BOOLEAN, Column, text
from sqlalchemy import DateTime as DateTimeTZ
from sqlmodel import Field, SQLModel


class Address(SQLModel, table=True):
    __tablename__ = "address"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(index=True, unique=True, max_length=150, min_length=1)
    address_type_id: int = Field(index=True, foreign_key="address_type.id")
    database_name: Optional[str] = Field(max_length=50)
    schema_name: Optional[str] = Field(max_length=50)
    table_name: Optional[str] = Field(max_length=50)
    primary_key: Optional[str] = Field(max_length=50)
    deprecated: bool = Field(
        sa_column=Column(BOOLEAN, server_default=text("FALSE"), nullable=False)
    )

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
