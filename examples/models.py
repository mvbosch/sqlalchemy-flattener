from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, Uuid
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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
        SQLEnum(AccountType, name="bank_account_type", values_callable=get_enum_values), nullable=False
    )


class Category(Base):
    __tablename__ = "category"

    name: Mapped[str] = mapped_column(Text(), nullable=False)


class Contact(Base):
    __tablename__ = "contact"

    # data columns
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    email: Mapped[str] = mapped_column(Text(), nullable=True)
    # foreign keys
    address_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("address.id"), nullable=False)
    supplier_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("supplier.id"), nullable=False)
    # relationships
    address: Mapped[Address] = relationship(lazy="noload")
    supplier: Mapped["Supplier"] = relationship(lazy="noload", back_populates="contacts")


class Supplier(Base):
    __tablename__ = "supplier"

    # data columns
    created_at: Mapped[datetime] = mapped_column(DateTime())
    email: Mapped[str] = mapped_column(Text())
    name: Mapped[str] = mapped_column(Text())
    # foreign keys
    address_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("address.id"))
    bank_details_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("bank_details.id"))
    # relationships
    address: Mapped[Address] = relationship(lazy="noload")
    bank_details: Mapped[BankDetails] = relationship(lazy="noload")
    categories: Mapped[list[Category]] = relationship(lazy="noload", secondary="supplier_category")
    contacts: Mapped[list[Contact]] = relationship(lazy="noload", back_populates="supplier")


class SupplierCategory(Base):
    """Supplier to category association table."""

    __tablename__ = "supplier_category"

    supplier_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("supplier.id"))
    category_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("category.id"))
