# This should be only one line. If it must be multi-line, indent the second
# line onwards to keep the PKG-INFO file format intact.
"""Batou components for managing source code in a development deployment.
"""

from setuptools import setup, find_packages

setup(
    name='batou_scm',
    version='1.0b1',

    python_requires='>=3.6, <4',
    install_requires=[
        'batou >= 2.0dev0',
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
    url='https://github.com/gocept/batou_scm',

    keywords='batou source code development checkout clone buildout',
    classifiers="""\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Zope Public License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Topic :: Software Development :: Build Tools
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(name).read() for name in (
        'README.rst',
        'HACKING.rst',
        'CHANGES.rst',
    )),

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
