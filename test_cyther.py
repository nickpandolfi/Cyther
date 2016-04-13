
from cyther import *
from subprocess import call

'''
@cyther

a = ''.join([str(x) for x in range(10)])
if a != '0123456789':
    raise CytherError("The @ code doesn't work correctly")
'''

core('example_file.pyx')
call(['python', 'cytherize.py', 'example_file.pyx', '-t'])

run(__file__)
run(__file__, timer=True)