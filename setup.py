# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import os.path
import re
import sys
import subprocess
from glob import glob

from setuptools import find_packages
from setuptools import setup

name = 'ngoschema'
package = 'ngoschema'
description = 'model definition, management and code-generation'
url = 'https://github.com/numengo/python-ngoschema'
author = 'Cédric ROMAN'
author_email = 'roman@numengo.com'
license = 'GNU General Public License v3'


def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    init_py = open(os.path.join(dir_path, 'src', package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]",
                     init_py, re.MULTILINE).group(1)


version = get_version(package)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(os.path.join('src', package))
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]
    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

setup_requires = [
    'pathlib',
    'matrix',
    #'pytest-runner', 
]

install_requires = [
    'pathlib',
    'apipkg',
    'future',
    'python-gettext',
    'click',
    'configparser2',
    'appdirs',
    'jsonschema',
    'ruamel.yaml',
    'jinja2',
    'python-dateutil',
    'arrow',  
]

cmd = ['pip','install', '-q'] + [i for i in install_requires if '-' in i]
subprocess.check_call(cmd)
install_requires = [i for i in install_requires if not '-' in i]

test_requires = [
    'pytest',
    'pytest-logger', 
]

extras_requires = {
}
   
setup(
    name=name,
    version=version,
    license=license,
    description=description,
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author=author,
    author_email=author_email,
    url=url,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data=get_package_data(package),
    py_modules=[os.path.splitext(os.path.basename(p))[0] for p in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,    
    keywords=["models", "schemas", "datavalidation", "semantic", "mixins", "dataserialization"], 
    # python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,!=2.7.*,!=3.4.*,",
    setup_requires=setup_requires,
    install_requires=install_requires,
    requires=install_requires,
    tests_require=test_requires,
    extras_require=extras_requires,
    entry_points={
        'console_scripts': [

            'obj_manager=ngoschema.cli:obj_manager_cli',
        ]
    },
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',    
        'Programming Language :: Python :: 2.7',    
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
)

if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a {0} -m 'version {0}'".format(version))
    print("  git push --tags")
    sys.exit()
