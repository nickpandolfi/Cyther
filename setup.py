from distutils.core import setup

#python setup.py register -r pypi
#python setup.py sdist --formats=zip,gztar,bztar bdist_wininst check upload -r pypi

long_description = open('README.txt').read()

version = '0.4.1'

short_description = 'The Cross-Platform Cython/Python Compiler'

setup(name='Cyther',
      version=version,
      description=short_description,
      long_description=long_description,

      packages=['cyther'],
      data_files=[('', ['LICENSE.txt','TODO.txt'])],

      platforms=['Windows', 'MacOS', 'POSIX', 'Unix'],
      author='Nicholas C. Pandolfi',
      author_email='npandolfi@wpi.edu',
      url='https://github.com/nickpandolfi/Cyther',
      license='MIT',
      keywords=['Cyther', 'Cython', 'Python', 'MinGW32',
                'vcvarsall.bat', 'vcvarsall not found',
                'setup.py', 'gcc', 'Python 3',
                'user-friendly', 'command-line',
                'script', 'auto-compiler'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Topic :: Software Development :: Compilers',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Desktop Environment :: File Managers',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Cython',
          'License :: OSI Approved :: MIT License',
          ]

     )