#!/usr/bin/env python3


from setuptools import setup, find_packages


with open("README.md") as fp:
    readme = fp.read()


with open("LICENSE") as fp:
    license = fp.read()


setup(
    name="qas",
    version="0.1.0",
    description="a function test framework",
    long_description=readme,
    author="hatlonely",
    author_email="hatlonely@foxmail.com",
    url="https://github.com/hatlonely/qas",
    license=license,
    packages=find_packages(exclude=("tests", "docs", "tmp"))
)
