# SQLAlchemy Flattener

This tool allows you to have the DX of defining test data with the ORM - 
nested as deeply as you like - then recursively flattening that data to either 
python dicts for bulk inserts, or just raw SQL insert statements for maximum seeding speed between tests.

Works really well in conjunction with [polyfactory](https://github.com/litestar-org/polyfactory)

## Usage

```
$ sqlflat --help

usage: sqlflat [-h] [--format {dict,sql}] instances order output

Flatten SQLAlchemy ORM instances.

positional arguments:
  instances            The module namespace containing the model instances, e.g. `foo.bar.instance_list`
  order                The module namespace containing a sequence of table insert ordering.
  output               The output file path to write the flattened data to.

options:
  -h, --help           show this help message and exit
  --format {dict,sql}  The format to write the data in.
```

Where `insertion_ordering_list` is a list of model classes *or* `sqlalchemy.Table` instances, but not declarative model instances.
Take a look at the examples directory.
