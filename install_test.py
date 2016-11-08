import subprocess

"""
Use these commands to do it manually:

pip uninstall cyther
pip install -i https://testpypi.python.org/pypi cyther'
"""

try:
    subprocess.call(['C:'])
    subprocess.call(['pip', 'uninstall', 'cyther'])
    subprocess.call(['pip', 'install', '-i', 'https://testpypi.python.org/pypi', 'cyther'])
except Exception as e:
    print(e)

input()
