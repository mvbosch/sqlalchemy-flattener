from datetime import datetime
from uuid import UUID

import pytest

from examples.models import AccountType, Address, BankDetails, Category, Contact, Supplier


@pytest.fixture
def categories() -> list[Category]:
    return [
        Category(
            id=UUID("3674c73c-a967-493f-9a4b-5b70f78a5a99"),
            name="Baked goods",
        ),
        Category(
            id=UUID("f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7"),
            name="ISP",
        ),
    ]


@pytest.fixture
def supplier(categories: list[Category]) -> Supplier:
    return Supplier(
        id=UUID("2b7e7211-d2c7-4eb4-8c14-05ed58c77473"),
        name="Loros Grist",
        email="info@loros.example",
        created_at=datetime(2020, 2, 21),
        address_id=UUID("c5fb851f-63fd-4572-872c-3597186c9afe"),
        bank_details_id=UUID("ccd390cf-a74c-4897-a923-3d77ce1b97bf"),
        address=Address(
            id=UUID("c5fb851f-63fd-4572-872c-3597186c9afe"),
            line_1="Celestia",
        ),
        bank_details=BankDetails(
            id=UUID("ccd390cf-a74c-4897-a923-3d77ce1b97bf"),
            account_number="payusnothing",
            account_type=AccountType.CASH,
        ),
        categories=categories,
        contacts=[
            Contact(
                id=UUID("98a11210-949a-48ad-99c7-1d89c54c2a53"),
                name="Sveimann Glort",
                email="sveimann@loros.example",
                address_id=UUID("cd521f7e-df61-4079-b44d-35015b9b5110"),
                supplier_id=UUID("2b7e7211-d2c7-4eb4-8c14-05ed58c77473"),
                address=Address(
                    id=UUID("cd521f7e-df61-4079-b44d-35015b9b5110"),
                    line_1="The imperial road",
                ),
            ),
        ],
    )


@pytest.fixture
def supplier_categories(categories: list[Category]) -> list[Supplier]:
    return [
        Supplier(id=UUID("330b18d4-5b92-49e5-b899-394dafd19e95"), categories=categories),
        Supplier(id=UUID("ca8e7bb6-898f-47d4-98f8-e5b560ed364e"), categories=categories),
    ]
