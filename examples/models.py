from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, Table, Text, Uuid, func, select
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    column_property,
    mapped_column,
    relationship,
)


class AccountType(str, Enum):
    """Bank account types."""

    CASH = "cash"
    CREDIT = "credit"


def get_enum_values(enum_class: "Enum") -> list[Any]:
    """Retrieve a list of values associated with an Enum type."""
    return [e.value for e in enum_class]


class Base(DeclarativeBase):
    """Base for all SQLAlchemy models."""

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True)


class Address(Base):
    __tablename__ = "address"

    line_1: Mapped[str] = mapped_column(Text())


class BankDetails(Base):
    __tablename__ = "bank_details"

    account_number: Mapped[str] = mapped_column(Text(), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(
        SQLEnum(AccountType, name="bank_account_type", values_callable=get_enum_values),
        nullable=False,
    )


class Category(Base):
    __tablename__ = "category"

    name: Mapped[str] = mapped_column(Text())


class SupplierTag(str, Enum):
    CHEAP = "cheap"
    RELIABLE = "reliable"


class Contact(Base):
    __tablename__ = "contact"

    # data columns
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    email: Mapped[str] = mapped_column(Text(), nullable=True)
    # foreign keys
    address_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("address.id"), nullable=False
    )
    supplier_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("supplier.id"), nullable=False
    )
    # relationships
    address: Mapped[Address] = relationship(lazy="raise")
    supplier: Mapped["Supplier"] = relationship(lazy="raise", back_populates="contacts")


class Supplier(Base):
    __tablename__ = "supplier"

    # data columns
    created_at: Mapped[datetime] = mapped_column(DateTime())
    email: Mapped[str] = mapped_column(Text())
    name: Mapped[str] = mapped_column(Text())
    tags: Mapped[list[SupplierTag]] = mapped_column(
        MutableList.as_mutable(
            ARRAY(
                SQLEnum(
                    SupplierTag,
                    values_callable=lambda t: [e.value for e in t],
                    name="supplier_tag",
                )
            )
        )
    )
    # foreign keys
    address_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("address.id"))
    bank_details_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("bank_details.id"))
    # relationships
    address: Mapped[Address] = relationship(lazy="raise")
    bank_details: Mapped[BankDetails] = relationship(lazy="raise")
    categories: Mapped[list[Category]] = relationship(
        lazy="raise", secondary="supplier_category"
    )
    contacts: Mapped[list[Contact]] = relationship(
        lazy="raise", back_populates="supplier"
    )
    # arbitrary column property
    category_count: Mapped[int] = column_property(
        select(func.count(Category.id)).scalar_subquery()
    )


supplier_category_association = Table(
    "supplier_category",
    Base.metadata,
    Column("supplier_id", Uuid(), ForeignKey("supplier.id"), primary_key=True),
    Column("category_id", Uuid(), ForeignKey("category.id"), primary_key=True),
)

INSERT_ORDER = [
    Address,
    BankDetails,
    Category,
    Supplier,
    Contact,
    supplier_category_association,
]
