set -e

echo Checking formatting...
ruff format --check .

echo Checking linting...
ruff .

echo Running tests...
pytest
