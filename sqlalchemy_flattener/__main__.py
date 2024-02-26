import argparse

from .flattener import SQLAlchemyFlattener
from .writers import write_as_dict, write_as_sql


def main() -> None:
    parser = argparse.ArgumentParser(description="Flatten SQLAlchemy ORM instances.")
    parser.add_argument(
        "module",
        type=str,
        help="The module containing the SQLAlchemy ORM classes.",
    )
    parser.add_argument(
        "output",
        type=str,
        help="The output file to write the flattened data to.",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="sql",
        choices=["dict", "sql"],
        help="The format to write the data in.",
    )
    args = parser.parse_args()
    module = __import__(args.module)
    flattener = SQLAlchemyFlattener()
    data = flattener.flatten(module)
    if args.format == "dict":
        write_as_dict(data, args.output)
    else:
        write_as_sql(data, args.output)
