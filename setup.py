from setuptools import setup, find_packages

setup(name='provo',
      author='Arne Rümmler',
      version='0.1',
      description='Construct provenance graphs according to PROV-O',
      url='https://github.com/GeoinformationSystems/provo',
      packages=setuptools.find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
          #   "License :: OSI Approved :: GNU GPLv3"
      ],
      )
