from distutils.core import setup
from pathlib import Path
import sys

# require version of setuptools that supports find_namespace_packages
from setuptools import setup
try:
    from setuptools import find_namespace_packages
except ImportError:
    # the user has a downlevel version of setuptools.
    print('Error: palm requires setuptools v40.1.0 or higher.')
    print('Please upgrade setuptools with "pip install --upgrade setuptools" and try again')
    sys.exit(1)

# User-friendly description from README.md
this_directory = Path(__file__).parent
long_description = Path(this_directory, 'README.md').read_text()

setup(
    name='palm-dbt',
    version='0.0.1',
    description='dbt extension for Palm CLI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jake Beresford',
    author_email='jake.bereford@palmetto.com',
    url='',
    # Packages to include into the distribution
    packages=find_namespace_packages(include=['palm', 'palm.*']),
    package_data={'': ['*.md', '*.sql', '*.yaml', '*.yml']},
    include_package_data=True,
    # TODO: Make this work...
    # List of packages to install with this one
    install_requires=[
		'palm>=2.0.0'
	],
    license='',
)
