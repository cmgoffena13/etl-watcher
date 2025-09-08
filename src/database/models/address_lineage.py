from sqlalchemy import BigInteger, Column
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
