import os

from setuptools import find_packages, setup

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

README = open(os.path.join(SCRIPT_DIR, "README.md")).read()

setup(
    name="tosql",
    version="0.0.2",
    description="tosql - pipe data to sql queries",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/velicanu/tosql",
    author="Dragos Velicanu",
    author_email="d@velicanu.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["click", "pandas"],
    extras_require={
        "test": ["pytest"],
    },
    entry_points={
        "console_scripts": [
            "tosql=tosql:main",
        ]
    },
)
