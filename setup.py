try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


NAME = 'Cyther'
VERSION = '0.5.3'
SHORT_DESCRIPTION = 'The Cross-Platform Cython/Python Compiler'
LONG_DESCRIPTION = open('README.txt').read()
PACKAGES = ['cyther']
SCRIPTS = ['cytherize.py']
DATA_FILES = [('cyther', ['CHANGELOG.txt', 'README.txt', 'TODO.txt', 'LICENSE.txt'])]
PLATFORMS = ['Windows', 'MacOS', 'POSIX', 'Unix']
AUTHOR = 'Nicholas C. Pandolfi'
AUTHOR_EMAIL = 'npandolfi@wpi.edu'
URL = 'https://github.com/nickpandolfi/Cyther'
LICENSE = 'MIT'
KEYWORDS = ['Cyther', 'Cython', 'Python', 'MinGW32',
            'vcvarsall.bat', 'vcvarsall not found',
            'setup.py', 'gcc', 'Python 3',
            'user-friendly', 'command-line',
            'script', 'auto-compiler']
CLASSIFIERS = ['Development Status :: 4 - Beta',
               'Environment :: Console',
               'Topic :: Software Development :: Compilers',
               'Topic :: Software Development :: Build Tools',
               'Topic :: Desktop Environment :: File Managers',
               'Intended Audience :: Developers',
               'Intended Audience :: Science/Research',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3.5',
               'Programming Language :: Python :: 3.4',
               'Programming Language :: Python :: 3.3',
               'Programming Language :: Cython',
               'License :: OSI Approved :: MIT License']

setup(name=NAME,
      version=VERSION,
      description=SHORT_DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      packages=PACKAGES,
      scripts=SCRIPTS,
      data_files=DATA_FILES,
      platforms=PLATFORMS,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      license=LICENSE,
      keywords=KEYWORDS,
      classifiers=CLASSIFIERS)
