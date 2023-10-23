from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from enum import Enum


def get_enum_values(enum_class: "Enum") -> list[Any]:
    """Retrieve a list of values associated with an Enum type."""
    return [e.value for e in enum_class]
