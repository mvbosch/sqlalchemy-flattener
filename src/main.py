from collections.abc import Sequence
from datetime import date
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Table, inspect
from sqlalchemy.orm import DeclarativeBase, KeyFuncDict, Relationship

# TODO: change to configuration or function arguments
INSERT_SECONDARY_ID = True
SECONDARY_ID_TYPE = "uuid"
SECONDARY_ID_COLUMN_NAME = "id"
STRINGIFY_UUIDS = True
STRINGIFY_DATES = True
USE_ENUM_VALUES = True

# TODO: improve global variable use
back_populates_tracker = []


def flatten_model_instance(
    model: DeclarativeBase, data_map: dict[Table, list[dict[str, Any]]]
) -> dict[Table, list[dict[str, Any]]]:
    """Flatten SQLAlchemy models to dictionaries ready for bulk insertion."""

    inspector = inspect(model)
    _append_mapping(data_map, model.__table__, model_columns_to_dict(model))

    for relationship in inspector.mapper.relationships:
        # avoid infinite recursion when circular references are present
        if relationship.back_populates:
            if (combination := {model.__tablename__, relationship.target.name}) in back_populates_tracker:
                continue

            back_populates_tracker.append(combination)
        if relationship.uselist:
            collection = getattr(model, relationship.key)
            if isinstance(collection, KeyFuncDict):
                collection = collection.values()
            for child in collection:
                # recursive flattening
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
        secondary_dict[SECONDARY_ID_COLUMN_NAME] = str(uuid4()) if STRINGIFY_UUIDS else uuid4()

    return secondary_dict


def get_data_mapping(data: DeclarativeBase | Sequence[DeclarativeBase]) -> dict[Table, list[dict[str, Any]]]:
    """Flatten SQLAlchemy models to dictionaries ready for bulk insertion."""

    if not isinstance(data, Sequence):
        data = [data]

    data_map = {}
    for model in data:
        data_map = flatten_model_instance(model, data_map)

    return deduplicate_data_mapping(data_map)


def deduplicate_data_mapping(data_map: dict[Table, list[dict[str, Any]]]) -> dict[Table, list[dict[str, Any]]]:
    """Deduplicate data mapping values."""

    return {table: [dict(t) for t in {tuple(d.items()) for d in values}] for table, values in data_map.items()}


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
