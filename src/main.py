from collections.abc import Sequence
from datetime import date
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Table, inspect
from sqlalchemy.orm import DeclarativeBase, Relationship

# set these as settings or arguments
INSERT_SECONDARY_ID = True
SECONDARY_ID_TYPE = "uuid"
SECONDARY_ID_COLUMN_NAME = "id"
STRINGIFY_UUIDS = True
STRINGIFY_DATES = True
USE_ENUM_VALUES = True


def flatten_model_instance(
    model: DeclarativeBase, data_map: dict[Table, list[dict[str, Any]]]
) -> dict[Table, list[dict[str, Any]]]:
    """Flatten SQLAlchemy models to dictionaries ready for bulk insertion."""

    inspector = inspect(model)
    _append_mapping(data_map, model.__table__, model_columns_to_dict(model))

    for relationship in inspector.mapper.relationships:
        if relationship.uselist:
            for child in getattr(model, relationship.key):
                data_map = flatten_model_instance(child, data_map)
                if relationship.secondary is not None:
                    secondary_dict = generate_secondary_row(relationship, model, child)
                    _append_mapping(data_map, relationship.secondary, secondary_dict)
        else:
            if (child := getattr(model, relationship.key)) is not None:
                data_map = flatten_model_instance(child, data_map)

    return data_map


def _append_mapping(data_map: dict[Table, list[dict[str, Any]]], table: Table, data_row: dict[str, Any]) -> Any:
    if table not in data_map:
        data_map[table] = []
    data_map[table].append(data_row)
    return data_map


def generate_secondary_row(relationship: Relationship, parent: DeclarativeBase, child: DeclarativeBase):
    secondary_dict = {}
    for column in relationship.remote_side:
        foreign_key = next(iter(column.foreign_keys))
        secondary_dict[column.key] = (
            getattr(parent, foreign_key.column.key)
            if foreign_key.column.table == parent.__table__
            else getattr(child, foreign_key.column.key)
        )
    if INSERT_SECONDARY_ID:
        secondary_dict[SECONDARY_ID_COLUMN_NAME] = uuid4()

    return secondary_dict


def get_data_mapping(data: DeclarativeBase | Sequence[DeclarativeBase]) -> dict[Table, list[dict[str, Any]]]:
    """Flatten SQLAlchemy models to dictionaries ready for bulk insertion."""

    if not isinstance(data, Sequence):
        data = [data]

    data_map = {}
    for model in data:
        data_map = flatten_model_instance(model, data_map)

    return data_map


def write_mapping(data: dict[Table, list[dict[str, Any]]], path: str) -> None:
    """Write a data mapping to a file."""

    with open(path, "w") as file:
        for table, value_list in data.items():
            file.write(f"{table.name} = {value_list}\n")


def model_columns_to_dict(
    model: DeclarativeBase
) -> dict[str, Any]:
    """Convert a SQLAlchemy model to a dictionary."""

    inspector = inspect(model)

    mapping = {}
    for column in inspector.mapper.column_attrs:
        value = getattr(model, column.key)
        if USE_ENUM_VALUES and isinstance(value, Enum):
            mapping[column.key] = value.value
            continue
        if STRINGIFY_DATES and isinstance(value, date):
            mapping[column.key] = str(value)
            continue
        if STRINGIFY_UUIDS and isinstance(value, UUID):
            mapping[column.key] = str(value)
            continue

        mapping[column.key] = value

    return mapping
