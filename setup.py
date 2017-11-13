# This should be only one line. If it must be multi-line, indent the second
# line onwards to keep the PKG-INFO file format intact.
"""Batou components for managing source code in a development deployment.
"""

from setuptools import setup, find_packages
import glob


setup(
    name='batou_scm',
    version='0.5',

    install_requires=[
        'batou >= 1.3',
    ],

    extras_require={
        'test': [
            'mock',
        ],
    },

    entry_points={
        'console_scripts': [
            # 'binary-name = batou_scm.module:function'
        ],
    },

    author='gocept <mail@gocept.com>',
    author_email='mail@gocept.com',
    license='ZPL 2.1',
    url='https://bitbucket.org/gocept/batou_scm/',

    keywords='batou source code development checkout clone buildout',
    classifiers="""\
License :: OSI Approved :: Zope Public License
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 2 :: Only
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(name).read() for name in (
        'README.txt',
        'HACKING.txt',
        'CHANGES.txt',
    )),

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    data_files=[('', glob.glob('*.txt'))],
    zip_safe=False,
)
