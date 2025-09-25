from sqlalchemy import BigInteger, Column, PrimaryKeyConstraint
from sqlmodel import Field, Index, SQLModel


class AddressLineage(SQLModel, table=True):
    __tablename__ = "address_lineage"

    id: int | None = Field(
        sa_column=Column(BigInteger, default=None, primary_key=True, nullable=False)
    )
    pipeline_id: int = Field(foreign_key="pipeline.id")
    source_address_id: int = Field(foreign_key="address.id")
    target_address_id: int = Field(foreign_key="address.id")

    __table_args__ = (
        Index(
            "ix_address_lineage_source_target",
            "source_address_id",
            "target_address_id",
            unique=True,
        ),
        Index(
            "ix_address_lineage_target_source",
            "target_address_id",
            "source_address_id",
            unique=True,
        ),
        Index(
            "ix_address_lineage_pipeline",
            "pipeline_id",
        ),
    )


class AddressLineageClosure(SQLModel, table=True):
    __tablename__ = "address_lineage_closure"

    source_address_id: int = Field(foreign_key="address.id")
    target_address_id: int = Field(foreign_key="address.id")
    depth: int

    __table_args__ = (
        PrimaryKeyConstraint("source_address_id", "target_address_id"),
        Index(
            "ix_address_lineage_closure_depth_source",
            "source_address_id",
            "depth",
            postgresql_include=["target_address_id"],
        ),
        Index(
            "ix_address_lineage_closure_depth_target",
            "target_address_id",
            "depth",
            postgresql_include=["source_address_id"],
        ),
    )
