set -e
set -x

rm -rf build/ dist/
python setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/* -u __token__ -p $PYPI_TOKEN
