from setuptools import find_packages, setup

setup(name='provo',
      author='Arne Rümmler',
      version='0.1.0',
      description='Construct  PROV-O compliant provenance graphs.',
      url='https://github.com/rue-a/provo',
      packages=find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: GNU GPLv3"
      ],
      )
