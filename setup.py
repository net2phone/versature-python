# -*- coding: utf-8 -*-
"""
Versature's Rest API
------------

"""
from setuptools import setup, find_packages


setup(
    name='Integrate API Library',
    version='1.0.0',
    url='https://github.com/Versature/integrateapilibrary.git',
    author='David Ward',
    author_email='dward@versature.com',
    description='A library for the Versature API',
    long_description=__doc__,
    py_modules=['versature api'],
    packages=find_packages(exclude=['test']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'requests>=2.5.0'
    ]
)