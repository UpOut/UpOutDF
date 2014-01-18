# coding: utf-8

from setuptools import setup, find_packages
import sys

from upoutdf import __version__

setup(
	name = 'upoutdf',
	version = __version__,
	description = 'UpOut DateFormat Parsing library',
	author = 'William King',
	author_email = 'will@upout.com',
	zip_safe = False,
	include_package_data = True,
	packages=find_packages(),
	install_requires=['python-dateutil','pytz']
)