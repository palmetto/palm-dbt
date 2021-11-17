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
    version='0.0.3',
    description='dbt extension for Palm CLI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Palmetto - Data & Analytics team',
    author_email='data-analytics-team@palmetto.com',
    url='https://github.com/palmetto/palm-dbt',
    packages=find_namespace_packages(include=['palm', 'palm.*']),
    package_data={'': ['*.md', '*.sql', '*.yaml', '*.yml']},
    install_requires=[
		'palmcli>=2.0.0'
	],    
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
    ],
)
