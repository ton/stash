import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'shelve',
    version = '0.0.1',
    author = 'Ton van den Heuvel',
    author_email = 'tonvandenheuvel@gmail.com',
    description = ('Shelve changes for source code repositories similar to `git stash`.'),
    license = 'BSD',
    packages=['shelf'],
    long_description=read('README.md'),
    scripts=['scripts/shelve.py'],
    data_files=[('/etc/bash_completion.d/', ['shelve-completion.bash'])],
    url='https://github.com/ton/shelve',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities',
    ],
)
