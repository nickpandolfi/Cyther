from cyther import *
from subprocess import call


core('example_file.pyx')
call(['python', 'cytherize.py', 'example_file.pyx',  '-t'])
core('-h')