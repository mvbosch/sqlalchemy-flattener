from __future__ import annotations

from unittest.mock import ANY

from sqlalchemy_flattener import flatten
from examples.models import (
    Address,
    BankDetails,
    Category,
    Contact,
    Supplier,
    SupplierCategory,
)


def test_flatten_model_instance(supplier: Supplier) -> None:
    data = flatten(supplier)

    assert data[Supplier.__table__] == [
        {
            "created_at": "2020-02-21 00:00:00",
            "email": "info@loros.example",
            "name": "Loros Grist",
            "address_id": "c5fb851f-63fd-4572-872c-3597186c9afe",
            "bank_details_id": "ccd390cf-a74c-4897-a923-3d77ce1b97bf",
            "id": "2b7e7211-d2c7-4eb4-8c14-05ed58c77473",
        }
    ]
    assert len(data[Address.__table__]) == 2
    assert all(
        d in data[Address.__table__]
        for d in [
            {"line_1": "Celestia", "id": "c5fb851f-63fd-4572-872c-3597186c9afe"},
            {
                "line_1": "The imperial road",
                "id": "cd521f7e-df61-4079-b44d-35015b9b5110",
            },
        ]
    )
    assert data[BankDetails.__table__] == [
        {
            "account_number": "payusnothing",
            "account_type": "cash",
            "id": "ccd390cf-a74c-4897-a923-3d77ce1b97bf",
        }
    ]
    assert len(data[Category.__table__]) == 2
    assert all(
        d in data[Category.__table__]
        for d in [
            {"name": "Baked goods", "id": "3674c73c-a967-493f-9a4b-5b70f78a5a99"},
            {"name": "ISP", "id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7"},
        ]
    )
    assert len(data[SupplierCategory.__table__]) == 2
    assert all(
        d in data[SupplierCategory.__table__]
        for d in [
            {
                "supplier_id": "2b7e7211-d2c7-4eb4-8c14-05ed58c77473",
                "category_id": "3674c73c-a967-493f-9a4b-5b70f78a5a99",
                "id": ANY,
            },
            {
                "supplier_id": "2b7e7211-d2c7-4eb4-8c14-05ed58c77473",
                "category_id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7",
                "id": ANY,
            },
        ]
    )
    assert data[Contact.__table__] == [
        {
            "name": "Sveimann Glort",
            "email": "sveimann@loros.example",
            "address_id": "cd521f7e-df61-4079-b44d-35015b9b5110",
            "supplier_id": "2b7e7211-d2c7-4eb4-8c14-05ed58c77473",
            "id": "98a11210-949a-48ad-99c7-1d89c54c2a53",
        }
    ]


def test_dedupe_many_to_many(supplier_categories: list[Supplier]) -> None:
    data = flatten(supplier_categories)
    assert len(data[Category.__table__]) == 2
    assert all(
        d in data[Category.__table__]
        for d in [
            {"name": "Baked goods", "id": "3674c73c-a967-493f-9a4b-5b70f78a5a99"},
            {"name": "ISP", "id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7"},
        ]
    )
    assert len(data[SupplierCategory.__table__]) == 4
    assert all(
        d in data[SupplierCategory.__table__]
        for d in [
            {
                "supplier_id": "330b18d4-5b92-49e5-b899-394dafd19e95",
                "category_id": "3674c73c-a967-493f-9a4b-5b70f78a5a99",
                "id": ANY,
            },
            {
                "supplier_id": "330b18d4-5b92-49e5-b899-394dafd19e95",
                "category_id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7",
                "id": ANY,
            },
            {
                "supplier_id": "ca8e7bb6-898f-47d4-98f8-e5b560ed364e",
                "category_id": "3674c73c-a967-493f-9a4b-5b70f78a5a99",
                "id": ANY,
            },
            {
                "supplier_id": "ca8e7bb6-898f-47d4-98f8-e5b560ed364e",
                "category_id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7",
                "id": ANY,
            },
        ]
    )
