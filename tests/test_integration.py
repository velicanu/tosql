import json
import os
import subprocess
import tempfile

CSV_DATA = """"Data.Precipitation","Date.Full","Date.Month","Date.Week of","Date.Year","Station.City","Station.Code","Station.Location","Station.State","Data.Temperature.Avg Temp","Data.Temperature.Max Temp","Data.Temperature.Min Temp","Data.Wind.Direction","Data.Wind.Speed"
"0.0","2016-01-03","1","3","2016","Birmingham","BHM","Birmingham, AL","Alabama","39","46","32","33","4.33"
"0.0","2016-01-03","1","3","2016","Huntsville","HSV","Huntsville, AL","Alabama","39","47","31","32","3.86"
"""


JSON_DATA = [
    {
        "Data.Precipitation": 0.0,
        "Date.Full": "2016-01-03",
        "Date.Month": 1,
        "Date.Week of": 3,
        "Date.Year": 2016,
        "Station.City": "Birmingham",
        "Station.Code": "BHM",
        "Station.Location": "Birmingham, AL",
        "Station.State": "Alabama",
        "Data.Temperature.Avg Temp": 39,
        "Data.Temperature.Max Temp": 46,
        "Data.Temperature.Min Temp": 32,
        "Data.Wind.Direction": 33,
        "Data.Wind.Speed": 4.33,
    },
    {
        "Data.Precipitation": 0.0,
        "Date.Full": "2016-01-03",
        "Date.Month": 1,
        "Date.Week of": 3,
        "Date.Year": 2016,
        "Station.City": "Huntsville",
        "Station.Code": "HSV",
        "Station.Location": "Huntsville, AL",
        "Station.State": "Alabama",
        "Data.Temperature.Avg Temp": 39,
        "Data.Temperature.Max Temp": 47,
        "Data.Temperature.Min Temp": 31,
        "Data.Wind.Direction": 32,
        "Data.Wind.Speed": 3.86,
    },
]


def test_get_df_csv_stdin():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input = os.path.join(tmpdir, "input")
        tmp_output = os.path.join(tmpdir, "output")
        with open(tmp_input, "w") as f:
            f.write(CSV_DATA)

        cmd = f"""cat {tmp_input} | tosql "SELECT * FROM a" > {tmp_output}  """
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        ps.wait()

        actual = [json.loads(line) for line in open(tmp_output)]
        assert actual == JSON_DATA


def test_get_df_csv_option():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input = os.path.join(tmpdir, "input")
        tmp_output = os.path.join(tmpdir, "output")
        with open(tmp_input, "w") as f:
            f.write(CSV_DATA)

        cmd = f"""tosql -i {tmp_input} "SELECT * FROM a" > {tmp_output}  """
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        ps.wait()

        actual = [json.loads(line) for line in open(tmp_output)]
        assert actual == JSON_DATA


def test_get_df_json_option_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input = os.path.join(tmpdir, "input")
        tmp_output = os.path.join(tmpdir, "output")
        with open(tmp_input, "w") as f:
            for line in JSON_DATA:
                f.write(f"{json.dumps(line)}\n")

        cmd = f"""tosql -i {tmp_input} -o {tmp_output} "SELECT * FROM a" """
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        ps.wait()

        actual = [json.loads(line) for line in open(tmp_output)]
        assert actual == JSON_DATA


SPACE_DATA = """Permissions Size User           Date Modified Name
drwxr-xr-x     - root 31 Jan 18:06  build
.rw-r--r--   846 root 31 Jan 19:13  setup.py
"""

EXPECTED_SPACE_DATA = [
    {
        "Permissions": "-",
        "Size": "root",
        "User": 31,
        "Date": "Jan",
        "Modified": "18:06",
        "Name": "build",
    },
    {
        "Permissions": "846",
        "Size": "root",
        "User": 31,
        "Date": "Jan",
        "Modified": "19:13",
        "Name": "setup.py",
    },
]


def test_get_df_space_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input = os.path.join(tmpdir, "input")
        tmp_output = os.path.join(tmpdir, "output")
        with open(tmp_input, "w") as f:
            f.write(SPACE_DATA)

        cmd = f"""cat {tmp_input} | tosql "SELECT * FROM a" > {tmp_output}  """
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        ps.wait()

        actual = [json.loads(line) for line in open(tmp_output)]
        assert actual == EXPECTED_SPACE_DATA


SQL_QUERY = """SELECT * FROM a WHERE name = "setup.py"
"""


def test_get_df_space_with_sql_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input = os.path.join(tmpdir, "input")
        tmp_output = os.path.join(tmpdir, "output")
        sql_file = os.path.join(tmpdir, "sql")
        with open(sql_file, "w") as f:
            f.write(SQL_QUERY)
        with open(tmp_input, "w") as f:
            f.write(SPACE_DATA)

        cmd = f"""cat {tmp_input} | tosql -f {sql_file} > {tmp_output}  """
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        ps.wait()

        actual = [json.loads(line) for line in open(tmp_output)]
        assert actual == [EXPECTED_SPACE_DATA[1]]


SPACE_DATA_NO_HEADER = """-rw-r--r--  1 dragosvelicanu  staff      846 Jan 31 19:13 setup.py
drwxr-xr-x  5 dragosvelicanu  staff      160 Jan 31 19:49 tests
"""

EXPECTED_SPACE_DATA_NO_HEADER_COLS = [
    {
        "perm": "-rw-r--r--",
        "link": 1,
        "user": "dragosvelicanu",
        "group": "staff",
        "size": 846,
        "mon": "Jan",
        "day": 31,
        "hour": "19:13",
        "name": "setup.py",
    },
    {
        "perm": "drwxr-xr-x",
        "link": 5,
        "user": "dragosvelicanu",
        "group": "staff",
        "size": 160,
        "mon": "Jan",
        "day": 31,
        "hour": "19:49",
        "name": "tests",
    },
]


def test_get_df_space_data_cols():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input = os.path.join(tmpdir, "input")
        tmp_output = os.path.join(tmpdir, "output")
        with open(tmp_input, "w") as f:
            f.write(SPACE_DATA_NO_HEADER)

        cmd = f"""cat {tmp_input} | tosql -c perm,link,user,group,size,mon,day,hour,name "SELECT * FROM a" > {tmp_output}  """
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        ps.wait()

        actual = [json.loads(line) for line in open(tmp_output)]
        assert actual == EXPECTED_SPACE_DATA_NO_HEADER_COLS


EXPECTED_SPACE_DATA_NO_HEADER_AUTO = [
    {
        "c_a": "-rw-r--r--",
        "c_b": 1,
        "c_c": "dragosvelicanu",
        "c_d": "staff",
        "c_e": 846,
        "c_f": "Jan",
        "c_g": 31,
        "c_h": "19:13",
        "c_i": "setup.py",
    },
    {
        "c_a": "drwxr-xr-x",
        "c_b": 5,
        "c_c": "dragosvelicanu",
        "c_d": "staff",
        "c_e": 160,
        "c_f": "Jan",
        "c_g": 31,
        "c_h": "19:49",
        "c_i": "tests",
    },
]


def test_get_df_space_data_auto():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input = os.path.join(tmpdir, "input")
        tmp_output = os.path.join(tmpdir, "output")
        with open(tmp_input, "w") as f:
            f.write(SPACE_DATA_NO_HEADER)

        cmd = f"""cat {tmp_input} | tosql --auto "SELECT * FROM a" > {tmp_output}  """
        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        ps.wait()

        actual = [json.loads(line) for line in open(tmp_output)]
        assert actual == EXPECTED_SPACE_DATA_NO_HEADER_AUTO
