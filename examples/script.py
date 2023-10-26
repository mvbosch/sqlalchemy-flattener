from sqlalchemy_flattener import flatten, write_raw, write_sql

from .instances import nested_supplier

if __name__ == "__main__":
    data = flatten(nested_supplier)
    write_raw(data, "raw_dict.py")
    write_sql(data, "raw.sql")
