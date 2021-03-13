#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="dbserver",
    description="DBServer using flask framwork and pickle.",

    packages=find_packages(),

    install_requires=[
        'jwt',
        'requests',
        'click',
        'flask', 'flask_restful',
        'click_logging @ git+https://github.com/KnacKWursTKinG/click_logging@main',
    ],

    version="0.0.1",
    maintainer='Udo Bauer',
    maintainer_email='knackwurstking.tux@gmail.com',
    url='https://github.com/KnacKWursTKinG/dbserver',
)
