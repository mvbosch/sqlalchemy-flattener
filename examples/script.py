from sqlalchemy_flattener import SQLAlchemyFlattener
from sqlalchemy_flattener.writers import write_as_dict, write_as_sql
from .instances import nested_supplier

if __name__ == "__main__":
    flattener = SQLAlchemyFlattener()
    data = flattener.flatten(nested_supplier)
    write_as_dict(data, "raw_dict.py")
    write_as_sql(data, "raw.sql")
