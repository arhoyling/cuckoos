import os
import re
from setuptools import setup, find_packages


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def list_requirements():
    requirements = {}
    req_dir = os.path.join(os .getcwd(), 'requirements')
    for f in os.listdir(req_dir):
        req, ext = os.path.splitext(f)

        if ext != '.txt':
            continue

        requirements[req] = list()
        with open(os.path.join(req_dir, f)) as fd:
            for line in fd.readlines():
                requirements[req].append(line)
    return requirements

requires = list_requirements()

setup(
    name='cuckoos',
    version=get_version('cuckoos'),
    description='Package to create nested objects with method namespaces.',
    long_description=open('README.md').read(),
    author='Alex R Hoyling',
    author_email='alex.r.hoyling@gmail.com',
    platforms=['any'],
    license='BSD',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=False,
    install_requires=requires['default'],
    tests_require=requires['test'],
    test_suite='tests',
    keywords=['python', 'meta', 'class', 'namespace'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
    ]
)
