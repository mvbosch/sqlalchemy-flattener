from __future__ import annotations

from examples.models import (
    Address,
    BankDetails,
    Category,
    Contact,
    Supplier,
    supplier_category_association,
    SupplierTag,
)
from sqlalchemy_flattener import SQLAlchemyFlattener


def test_flatten_model_instance(suppliers: Supplier) -> None:
    flattener = SQLAlchemyFlattener()
    data = flattener.flatten(suppliers)

    # column properties should not be present
    assert "category_count" not in data[Supplier.__table__][0]

    assert all(
        d in data[Supplier.__table__]
        for d in [
            {
                "created_at": "2020-02-21 00:00:00",
                "email": "info@loros.example",
                "name": "Loros Grist",
                "address_id": "c5fb851f-63fd-4572-872c-3597186c9afe",
                "bank_details_id": "ccd390cf-a74c-4897-a923-3d77ce1b97bf",
                "id": "2b7e7211-d2c7-4eb4-8c14-05ed58c77473",
                "tags": [SupplierTag.CHEAP, SupplierTag.RELIABLE],
            },
            {
                "created_at": "2020-02-21 00:00:00",
                "email": "info@yvon.example",
                "name": "Salvoss Yvon",
                "address_id": "c307f778-1888-4077-9888-55bce7738738",
                "bank_details_id": "0cb8bffb-7323-46de-88e0-3a9f3a7edfcf",
                "id": "8f4f00f7-3352-4579-84ef-e2f8a455afc3",
                "tags": None,
            },
        ]
    )
    assert len(data[Address.__table__]) == 4
    assert all(
        d in data[Address.__table__]
        for d in [
            {"line_1": "Celestia", "id": "c5fb851f-63fd-4572-872c-3597186c9afe"},
            {
                "line_1": "The imperial road",
                "id": "cd521f7e-df61-4079-b44d-35015b9b5110",
            },
            {"id": "c307f778-1888-4077-9888-55bce7738738", "line_1": "Hovallii Psot"},
            {
                "id": "b94ed931-45a9-4a9a-8456-a22efe797fc2",
                "line_1": "Another departure",
            },
        ]
    )
    assert all(
        d in data[BankDetails.__table__]
        for d in [
            {
                "account_number": "payusnothing",
                "account_type": "cash",
                "id": "ccd390cf-a74c-4897-a923-3d77ce1b97bf",
            },
            {
                "account_number": "payless",
                "account_type": "cash",
                "id": "0cb8bffb-7323-46de-88e0-3a9f3a7edfcf",
            },
        ]
    )
    assert len(data[Category.__table__]) == 2
    assert all(
        d in data[Category.__table__]
        for d in [
            {"name": "Baked goods", "id": "3674c73c-a967-493f-9a4b-5b70f78a5a99"},
            {"name": "ISP", "id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7"},
        ]
    )
    assert len(data[supplier_category_association]) == 4
    assert all(
        d in data[supplier_category_association]
        for d in [
            {
                "supplier_id": "2b7e7211-d2c7-4eb4-8c14-05ed58c77473",
                "category_id": "3674c73c-a967-493f-9a4b-5b70f78a5a99",
            },
            {
                "supplier_id": "2b7e7211-d2c7-4eb4-8c14-05ed58c77473",
                "category_id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7",
            },
            {
                "supplier_id": "8f4f00f7-3352-4579-84ef-e2f8a455afc3",
                "category_id": "3674c73c-a967-493f-9a4b-5b70f78a5a99",
            },
            {
                "supplier_id": "8f4f00f7-3352-4579-84ef-e2f8a455afc3",
                "category_id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7",
            },
        ]
    )
    assert all(
        d in data[Contact.__table__]
        for d in [
            {
                "name": "Sveimann Glort",
                "email": "sveimann@loros.example",
                "address_id": "cd521f7e-df61-4079-b44d-35015b9b5110",
                "supplier_id": "2b7e7211-d2c7-4eb4-8c14-05ed58c77473",
                "id": "98a11210-949a-48ad-99c7-1d89c54c2a53",
            },
            {
                "name": "Jevutte Nosk",
                "email": "jevutte@yvon.example",
                "address_id": "b94ed931-45a9-4a9a-8456-a22efe797fc2",
                "supplier_id": "8f4f00f7-3352-4579-84ef-e2f8a455afc3",
                "id": "97e9593f-4f15-40c2-932f-a0aa5b500f8b",
            },
        ]
    )


def test_dedupe_many_to_many(supplier_categories: list[Supplier]) -> None:
    flattener = SQLAlchemyFlattener()
    data = flattener.flatten(supplier_categories)
    assert len(data[Category.__table__]) == 2
    assert all(
        d in data[Category.__table__]
        for d in [
            {"name": "Baked goods", "id": "3674c73c-a967-493f-9a4b-5b70f78a5a99"},
            {"name": "ISP", "id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7"},
        ]
    )
    assert len(data[supplier_category_association]) == 4
    assert all(
        d in data[supplier_category_association]
        for d in [
            {
                "supplier_id": "330b18d4-5b92-49e5-b899-394dafd19e95",
                "category_id": "3674c73c-a967-493f-9a4b-5b70f78a5a99",
            },
            {
                "supplier_id": "330b18d4-5b92-49e5-b899-394dafd19e95",
                "category_id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7",
            },
            {
                "supplier_id": "ca8e7bb6-898f-47d4-98f8-e5b560ed364e",
                "category_id": "3674c73c-a967-493f-9a4b-5b70f78a5a99",
            },
            {
                "supplier_id": "ca8e7bb6-898f-47d4-98f8-e5b560ed364e",
                "category_id": "f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7",
            },
        ]
    )
