from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='provo',
      author='Arne Rümmler',
      version='0.2.0',
      description='Construct  PROV-O compliant provenance graphs.',
      long_description=long_description
      long_description_content_type='text/markdown'
      url='https://github.com/rue-a/provo',
      packages=find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3.11",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
      ],
      )
