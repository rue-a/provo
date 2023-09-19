# -*- coding: utf-8 -*-
"""
provo
-----

Construct  PROV-O compliant provenance graphs.
"""

from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent

setup(
    name="provo",
    author="Arne Rümmler",
    author_email="arne.ruemmler@gmail.com",
    version="1.1.3",
    description="Construct  PROV-O compliant provenance graphs.",
    url="https://github.com/rue-a/provo",
    packages=find_packages(".", exclude=["tests", "tests.*"]),
    install_requires=["rdflib", "validators", "uuid"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.09",
)
