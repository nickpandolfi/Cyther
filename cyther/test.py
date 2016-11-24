
import cyther
import subprocess
from .tools import generateBatches


def test_cyther():
    #An info call to display helpful info in log
    cyther.info(None)
    cyther.core('cyther info')
    subprocess.call(['cyther', 'info'])

    #Do a core, command line, and function run
    #subprocess.call(['cyther', 'build', 'example_file.pyx'])

    print('<@test.py> All compilation tests have been passed')


def test_utilities():
    t = {
        'a': ['b'],
        'b': ['c'],
        'c': ['d', 'e', 'f', 'g'],
        'd': ['e', 'g', 'j'],
        'e': ['f'],
        'f': ['i', 'j'],
        'g': ['j'],
        'h': ['i'],
        'i': ['j'],
        'j': ['q'],
    }
    g = ['q']
    batches = generateBatches(t, g)
    assert batches == [{'j'}, {'i', 'g'}, {'f', 'h'}, {'e'}, {'d'}, {'c'}, {'b'}, {'a'}]
    return


if __name__ == '__main__':
    test_cyther()
