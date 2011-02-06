#!/usr/bin/env python2
"""
    clover.roulette
    ~~~~~~~~~~~~~~~

    Generate color schemes from COLOURlovers palettes.
"""
from setuptools import setup, find_packages
from clover.roulette import __version__


setup(
    name="clover-roulette",
    version=__version__,
    license="BSD",
    description=__doc__,
    packages=["clover"],
    namespace_packages=["clover"]
)
