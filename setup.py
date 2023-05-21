#!/usr/bin/python3 python3.11

import os

from setuptools import setup

setup(
    name="cross-docking-project",
    version="0.0.1",
    description="",
    long_description=open(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")
    ).read(),
    long_description_content_type="text/markdown",
    author="Vinícius Ferreira Aguiar",
    packages=["cross-docking"],
    install_requires=[""],
)
