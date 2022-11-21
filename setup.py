# -*- coding: utf-8 -*-
"""
provo
-----

Construct  PROV-O compliant provenance graphs.
"""

from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "/misc/pypi_description.md").read_text()

setup(
    name="provo",
    author="Arne Rümmler",
    author_email="arne.ruemmler@gmail.com",
    version="0.2.1",
    description="Construct  PROV-O compliant provenance graphs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rue-a/provo",
    packages=find_packages('.', exclude=['tests', 'tests.*']),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.11"
)
