from sqlalchemy import BigInteger, Column, PrimaryKeyConstraint
from sqlmodel import Field, Index, SQLModel


class AddressLineageClosure(SQLModel, table=True):
    __tablename__ = "address_lineage_closure"

    source_address_id: int = Field(foreign_key="address.id")
    target_address_id: int = Field(foreign_key="address.id")
    depth: int

    __table_args__ = (PrimaryKeyConstraint("source_address_id", "target_address_id"),)
