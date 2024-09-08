#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "click==8.1.7",
    "rich==13.8.0",
    "requests==2.32.3",
    "pydantic==2.8.2",
    "basecampy3==0.7.2",
    "SQLAlchemy==2.0.34",
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest",
]

setup(
    author="Collin Meyers",
    author_email="cfmeyers@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    description="A CLI utility for interacting with Basecamp 4 API",
    entry_points={
        "console_scripts": [
            "tenzing=tenzing.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="tenzing",
    name="tenzing",
    packages=find_packages(include=["tenzing"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/cfmeyers/tenzing",
    version="0.1.0",
    zip_safe=False,
)
