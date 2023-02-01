# tosql - run sql queries on CLI data

`tosql` is a cli tool for running SQL queries on CLI data and outputting results to json
format. It can read/write from stdin/stdout so it should work fairly naturally.

## Setup

Install via pip:

```bash
pip install tosql
```

## Quick Start

Pipe any tabular data in and use `tosql` to run a sql query on it. The default table
name to select from is "df"

```bash
df | tosql "SELECT * FROM df LIMIT 2"
```

If you run `tosql` with no arguments it will "SELECT * FROM df" by default.

```bash
df | tosql
```

### CLI Options

`tosql` has several command line options to choose from, displyed by running with the
"--help" flag.

```bash
$ tosql --help
Usage: tosql [OPTIONS] [SQL]

Options:
  --version              Show the version and exit.
  -i, --input FILENAME   Input file, default stdin
  -o, --output TEXT      Output file, default stdout
  -f, --sql-file TEXT    File containing SQL query
  -t, --table-name TEXT  Table name  [default: df]
  -c, --cols TEXT        Column names, comma separated
  --auto                 Autogenerate column names: a b c ...
  --save                 Save the sql file to .tosql.db
  --help                 Show this message and exit.
```
