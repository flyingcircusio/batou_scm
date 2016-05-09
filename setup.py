# This should be only one line. If it must be multi-line, indent the second
# line onwards to keep the PKG-INFO file format intact.
"""Batou components for managing source code in a development deployment.
"""

from setuptools import setup, find_packages
import glob
import os.path


def project_path(*names):
    return os.path.join(os.path.dirname(__file__), *names)


setup(
    name='batou_scm',
    version='0.3.1',

    install_requires=[
        'batou >= 1.0b26.dev0',
    ],

    extras_require={
        'test': [
            'batou >= 1.2',
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
    long_description='\n\n'.join(open(project_path(name)).read() for name in (
        'README.txt',
        'HACKING.txt',
        'CHANGES.txt',
    )),

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    data_files=[('', glob.glob(project_path('*.txt')))],
    zip_safe=False,
)
