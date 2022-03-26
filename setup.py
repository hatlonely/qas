#!/usr/bin/env python3


from setuptools import setup, find_packages


with open("README.rst") as fp:
    readme = fp.read()


with open("LICENSE") as fp:
    license_ = fp.read()


setup(
    name="qas",
    version="1.0.8",
    description="A general, concurrent and extensible functional testing framework",
    long_description=readme,
    author="hatlonely",
    author_email="hatlonely@foxmail.com",
    url="https://github.com/hatlonely/qas",
    license=license_,
    packages=find_packages(exclude=("tests", "docs", "tmp", "ops", "build", "dist")),
    scripts=["bin/qas"],
    keywords=["qas"],
    install_requires=[
        "requests~=2.27.1",
        "PyYAML~=6.0",
        "colorama~=0.4.4",
        "tablestore~=5.1.0",
        "python-dateutil~=2.8.1",
        "aliyun-python-sdk-core~=2.13.36",
        "aliyun-python-sdk-core-v3~=2.13.33",
        "aliyunsdkcore~=1.0.3",
        "PyMySQL~=1.0.2",
        "redis~=4.1.0",
        "setuptools~=57.4.0",
        "durationpy~=0.5",
        "aliyun-mns-sdk~=1.1.6",
        "oss2~=2.15.0",
        "pymongo~=4.0.1",
        "Jinja2~=3.0.3",
        "Markdown~=3.3.6",
        "grpcio~=1.43.0",
        "grpcio-tools~=1.43.0",
        "protobuf~=3.19.3",
        "thrift~=0.15.0",
        "elasticsearch~=7.16.0",
        "aliyun-log-python-sdk~=0.7.5",
        "google-api-python-client~=2.39.0",
        "gcloud~=0.18.3",
    ],
)
