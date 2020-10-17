#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    README = fh.read()

setuptools.setup(
    name="ogr2pbf",
    version="0.0.1",
    license='MIT License',
    author="Roel Derickx",
    author_email="ogr2pbf.pypi@derickx.be",
    description="A tool for converting ogr-readable files like shapefiles into .osm or .pbf data",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/roelderickx/ogr2pbf",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ['ogr2pbf = ogr2pbf.ogr2pbf:main']
    },
    classifiers=[
        'Environment :: Console',
        'Topic :: Scientific/Engineering :: GIS',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

