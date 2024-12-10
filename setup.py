import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
	README = readme.read()

# allow setup.py to be run from any path
os.chdir(
	os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))
)

setup(
	name='qt-stylehelper',
	version='0.1.1',
	packages=[
		'qt_stylehelper',
		'qt_stylehelper.themes',
		'qt_stylehelper.resources',
		'qt_stylehelper.resources.icons',
	],
	author='Hayes Kwon',
	author_email='92khsang@gmail.com',
	maintainer='Hayes Kwon',
	maintainer_email='92khsang@gmail.com',
	download_url='https://github.com/92khsang/qt-stylehelper',
	install_requires=['Jinja2'],
	python_requires='>=3.12',
	include_package_data=True,
	license='BSD-2-Clause',
	description="Designed to simplify QT design in Python3. Inspired by qt-material",
	long_description=README,
	long_description_content_type='text/markdown',
	classifiers=[
		'License :: OSI Approved :: BSD License',
		'Programming Language :: Python :: 3.12',
	]
)
