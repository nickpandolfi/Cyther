import subprocess
import os

"""
TO USE BDIST_WHEEL YOU MUST HAVE THE MODULE 'WHEEL' INSTALLED
MUST INSTALL PANDOC: Go to 'http://pandoc.org/' and download the installer > This is not a python module!!!
Use python --user pypi.py to upload?????
"""

push_or_pull = input("Push or pull from pypi? (push/pull): ")

while push_or_pull not in ('push', 'pull'):
    push_or_pull = input("Incorrect response! Must either be 'pull' or 'push'\nTry again: ")

if push_or_pull == 'push':

    response = input("To the test, or real pypi? (test/real): ")

    while response not in ('test', 'real'):
        response = input("Incorrect response! Must either be 'test' or 'real'\nTry again: ")

    result = 'pypitest' if response == 'test' else 'pypi'

    subprocess.call(['pandoc', 'README.md', '-f', 'markdown',
                     '-t', 'rst', '-o', 'README.txt'])

    subprocess.call(['python', 'setup.py', 'sdist', '--formats=zip,gztar', 'bdist_wheel', 'bdist_wininst',
                     'check', 'upload', '-r', result])

    os.remove('README.txt')

else:
    subprocess.call(['pip', 'uninstall', 'cyther'])
    subprocess.call(['pip', 'install', '-i', 'https://testpypi.python.org/pypi', 'cyther'])

