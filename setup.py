# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# get version from __version__ variable in jwt_frappe/__init__.py
from jwt_frappe import __version__ as version

setup(
	name='jwt_frappe',
	version=version,
	description='auth with token for mobile and frontend applications ',
	author='ahmadragheb',
	author_email='Ahmedragheb75@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True
)
