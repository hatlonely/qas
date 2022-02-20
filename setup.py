#!/usr/bin/env python3


from setuptools import setup, find_packages


with open("README.rst") as fp:
    readme = fp.read()


with open("LICENSE") as fp:
    license_ = fp.read()


with open("requirements.txt") as fp:
    requires = [i.strip() for i in fp.readlines()]


setup(
    name="qas",
    version="1.0.1",
    description="A general, concurrent and extensible functional testing framework",
    long_description=readme,
    author="hatlonely",
    author_email="hatlonely@foxmail.com",
    url="https://github.com/hatlonely/qas",
    license=license_,
    packages=find_packages(exclude=("tests", "docs", "tmp", "ops", "build", "dist")),
    scripts=["bin/qas"],
    keywords=["qas"],
    install_requires=requires,
)
