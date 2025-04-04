#! /usr/bin/env python

import json
import os
import sqlite3
import string
import sys
import tempfile

import click
import pandas as pd


def get_df(input, cols, auto, sep) -> pd.DataFrame:
    """
    Tries to read the input file and return a dataframe.
    Will first try to read the input as a json file,
    If that doesn't work then it will try to read as a csv

    input: file object
    returns: a pandas dataframe
    """
    # first try inferring from the filename
    if input.name.endswith(".json"):
        return pd.read_json(input, lines=True)
    if input.name.endswith(".csv"):
        return pd.read_csv(input, engine="python", sep=sep)

    # next use heuristics
    with tempfile.TemporaryDirectory() as tmpdir:
        pre_input = os.path.join(tmpdir, "pre_input")
        with open(pre_input, "w") as out:
            out.write(input.read())
        first_line = [line for line in open(pre_input)][0]

        input_ = os.path.join(tmpdir, "_")
        with open(input_, "w") as out:
            if cols:
                out.write(" ".join(cols.split(",")) + "\n")
            elif auto:
                columns = [c for c in first_line.split(" ") if c]
                auto_headers = [
                    f"c_{col}" for _, col in zip(columns, string.ascii_lowercase)
                ]
                out.write(" ".join(auto_headers) + "\n")
            # needed to cache when reading from stdin
            out.write(open(pre_input).read())

        # first try reading json
        try:
            df = pd.read_json(input_, lines=True)
            # sometimes read_json will succeed on a csv file and renders
            # incorrectly as a single column dataframe
            if len(df.columns) > 1:
                return df
        except ValueError:
            pass

        # if that fails try reading as csv
        try:
            df = pd.read_csv(input_)
            if input.name == "<stdin>" and len(df.columns) < 2:
                pass
            else:
                return df
        except ValueError:
            pass

        csvd_filename = os.path.join(tmpdir, "csvd")
        with open(csvd_filename, "w") as out:
            with open(input_, "r") as input_file:
                for line in input_file:
                    csvd_line = chr(31).join([v for v in line.strip().split(" ") if v])
                    out.write(f"{csvd_line}\n")

        try:
            return pd.read_csv(csvd_filename, delimiter=chr(31))
        except ValueError:
            pass

    raise ValueError("could not parse the input")


def run_sql(query, dfs):
    with sqlite3.connect(":memory:") as conn:
        for df, table_name in zip(dfs, string.ascii_lowercase):
            df.to_sql(table_name, conn, index=False)
        out = pd.read_sql(query, conn)

    return out


def save_csv(df, output):
    df.to_csv(output if output else sys.stdout.buffer, index=False)


def save_json(df, output):
    records = df.to_dict(orient="records")
    if output:
        with open(output, "w") as out:
            for record in records:
                out.write(f"{json.dumps(record)}\n")
    else:
        for record in records:
            sys.stdout.buffer.write(f"{json.dumps(record)}\n".encode())


def save_db(df, table_name):
    if os.path.exists(".tosql.db"):
        os.remove(".tosql.db")
    conn = sqlite3.connect(".tosql.db")
    df.to_sql(table_name, conn, index=False)


@click.command()
@click.version_option(package_name="tosql")
@click.option(
    "-i",
    "--input",
    type=click.File(),
    default=["-"],
    multiple=True,
    help="Input file, default stdin",
)
@click.option("-o", "--output", type=str, help="Output file, default stdout")
@click.option("-f", "--sql-file", type=str, help="File containing SQL query")
@click.option("-c", "--cols", type=str, help="Column names, comma separated")
@click.option(
    "--auto",
    is_flag=True,
    default=False,
    help="Autogenerate column names: c_a c_b c_c ...",
)
@click.option(
    "--save", is_flag=True, default=False, help="Save the sql file to .tosql.db"
)
@click.option("--csv", is_flag=True, default=False, help="Output csv instead of json")
@click.option("-s", "--sep", type=str, help="Seperator for csv files")
@click.argument("sql", default="SELECT * FROM a")
def main(input, output, sql_file, cols, auto, save, csv, sep, sql):
    dfs_in = [get_df(input_, cols, auto, sep) for input_ in input]
    df_out = run_sql(open(sql_file).read() if sql_file else sql, dfs_in)

    if csv:
        save_csv(df_out, output)
    else:
        save_json(df_out, output)

    if save:
        save_db(dfs_in)


if __name__ == "__main__":
    main()
