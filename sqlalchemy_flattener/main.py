from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import inspect
from sqlalchemy.orm import KeyFuncDict

if TYPE_CHECKING:
    from sqlalchemy import Table
    from sqlalchemy.orm import DeclarativeBase, Relationship

__all__ = [
    "deduplicate_data_mapping",
    "flatten",
    "flatten_instance",
    "generate_secondary_row",
    "model_columns_to_dict",
    "write_raw",
    "write_sql",
]


# TODO: change to configuration or function arguments
INSERT_SECONDARY_ID = True
SECONDARY_ID_TYPE = "uuid"
SECONDARY_ID_COLUMN_NAME = "id"
STRINGIFY_UUIDS = True
STRINGIFY_DATES = True
USE_ENUM_VALUES = True


def flatten_instance(
    model: DeclarativeBase, data_map: dict[Table, list[dict[str, Any]]]
) -> dict[Table, list[dict[str, Any]]]:
    """Flatten SQLAlchemy models to dictionaries ready for bulk insertion."""

    inspector = inspect(model)
    _append_mapping(data_map, model.__table__, model_columns_to_dict(model))

    for relationship in inspector.mapper.relationships:
        if relationship.uselist:
            collection = getattr(model, relationship.key)
            if isinstance(collection, KeyFuncDict):
                collection = collection.values()
            for child in collection:
                if relationship.secondary is not None:
                    secondary_dict = generate_secondary_row(relationship, model, child)
                    # check that the secondary row is not already present - ID values could be random
                    if not (secondary_records := data_map.get(relationship.secondary)):
                        _append_mapping(
                            data_map, relationship.secondary, secondary_dict
                        )
                    elif not any(
                        {
                            k: v
                            for k, v in secondary_dict.items()
                            if k != SECONDARY_ID_COLUMN_NAME
                        }
                        == {
                            k: v
                            for k, v in record.items()
                            if k != SECONDARY_ID_COLUMN_NAME
                        }
                        for record in secondary_records
                    ):
                        _append_mapping(
                            data_map, relationship.secondary, secondary_dict
                        )
                # avoid infinite recursion when circular references are present
                if (entries := data_map.get(child.__table__)) and any(
                    str(entry.get("id")) == str(child.id) for entry in entries
                ):
                    continue
                # recursive flattening
                data_map = flatten_instance(child, data_map)

        else:
            if (child := getattr(model, relationship.key)) is not None:
                # avoid infinite recursion when circular references are present
                if (entries := data_map.get(child.__table__)) and any(
                    str(entry.get("id")) == str(child.id) for entry in entries
                ):
                    return data_map
                data_map = flatten_instance(child, data_map)

    return data_map


def _append_mapping(
    data_map: dict[Table, list[dict[str, Any]]], table: Table, data_row: dict[str, Any]
) -> Any:
    if table not in data_map:
        data_map[table] = []
    data_map[table].append(data_row)
    return data_map


def generate_secondary_row(
    relationship: Relationship, parent: DeclarativeBase, child: DeclarativeBase
) -> dict[str, Any]:
    """Generate rows for secondary a.k.a. association tables."""
    secondary_dict = {}
    for column in relationship.remote_side:
        foreign_key = next(iter(column.foreign_keys))
        secondary_dict[column.name] = (
            getattr(parent, foreign_key.column.name)
            if foreign_key.column.table == parent.__table__
            else getattr(child, foreign_key.column.name)
        )
        if STRINGIFY_UUIDS and isinstance(secondary_dict[column.name], UUID):
            secondary_dict[column.name] = str(secondary_dict[column.name])
    if INSERT_SECONDARY_ID:
        secondary_dict[SECONDARY_ID_COLUMN_NAME] = (
            str(uuid4()) if STRINGIFY_UUIDS else uuid4()
        )

    return secondary_dict


def flatten(
    data: DeclarativeBase | Sequence[DeclarativeBase],
) -> dict[Table, list[dict[str, Any]]]:
    """Flatten SQLAlchemy models to dictionaries ready for bulk insertion."""

    if not isinstance(data, Sequence):
        data = [data]

    data_map = {}
    for model in data:
        data_map = flatten_instance(model, data_map)

    return deduplicate_data_mapping(data_map)


def deduplicate_data_mapping(
    data_map: dict[Table, list[dict[str, Any]]],
) -> dict[Table, list[dict[str, Any]]]:
    """Deduplicate data mapping values."""

    return {
        table: [dict(t) for t in {tuple(d.items()) for d in values}]
        for table, values in data_map.items()
    }


def write_raw(data: dict[Table, list[dict[str, Any]]], path: str) -> None:
    """Write a data mapping to a file."""

    with open(path, "w") as file:
        for table, value_list in data.items():
            file.write(f"{table.name} = {value_list}\n")


def write_sql(data: dict[Table, list[dict[str, Any]]], path: str) -> None:
    """Write a datamapping as raw SQL `INSERT` statements."""

    with open(path, "w") as file:
        for table, data_list in data.items():
            value_list = []
            for data_map in data_list:
                values = []
                for item in data_map.values():
                    if item is None:
                        value = "NULL"
                    elif isinstance(item, str):
                        value = f"""'{item.replace("'", "''")}'"""
                    elif isinstance(item, date | bool):
                        value = f"'{item}'"
                    else:
                        value = str(item)
                    values.append(value)
                value_list.append(f'    ({", ".join(values)})')
            value_string = ",\n".join(value_list)
            file.write(
                f"""\nINSERT INTO "{table.name}" ({", ".join(data_list[0].keys())})\nVALUES\n{value_string};\n"""
            )


def model_columns_to_dict(model: DeclarativeBase) -> dict[str, Any]:
    """Convert a SQLAlchemy model to a dictionary."""

    inspector = inspect(model)

    mapping = {}
    for column in inspector.mapper.column_attrs:
        value = getattr(model, column.key)
        if USE_ENUM_VALUES and isinstance(value, Enum):
            mapping[column.expression.key] = value.value
            continue
        if STRINGIFY_DATES and isinstance(value, date):
            mapping[column.expression.key] = str(value)
            continue
        if STRINGIFY_UUIDS and isinstance(value, UUID):
            mapping[column.expression.key] = str(value)
            continue

        mapping[column.expression.key] = value

    return mapping
