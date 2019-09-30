from setuptools import setup, find_packages
from codecs import open
import os
from DockerBuildSystem import VersionTools

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    reqLines = f.readlines()
REQUIREMENTS = [reqLine.replace('\r', '').replace('\n', '') for reqLine in reqLines]
VERSION = VersionTools.GetVersionFromChangelog('CHANGELOG.md')

PACKAGE_NAME = 'DockerFeed'
PACKAGE_CONSOLE_NAME = 'dockerf'
setup(
    name=PACKAGE_NAME,  # Required
    version=VERSION,  # Required
    description='Docker Feed tool',  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional
    url='http://vd-tfs03:8080/tfs/DefaultCollection/DIPS/_git/DockerFeed',  # Optional
    author='DIPS AS',  # Optional
    author_email='hha@dips.no,heh@dips.no',  # Optional
    include_package_data=True,
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='Docker Feed',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', '*tests']),  # Required
    install_requires=REQUIREMENTS,  # Optional

    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    entry_points={  # Optional
        'console_scripts': [
            f'{PACKAGE_CONSOLE_NAME}={PACKAGE_NAME}:main',
        ],
    }
)
