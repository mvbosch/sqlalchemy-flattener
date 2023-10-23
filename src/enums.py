from enum import Enum


class AccountType(str, Enum):
    """Bank account types."""

    CASH = "cash"
    CREDIT = "credit"
