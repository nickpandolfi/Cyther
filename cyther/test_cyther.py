
import cyther
import subprocess


def test_cyther():
    subprocess.call(['cytherize', 'example_file.pyx', '-s', '-e'])
    cyther.core('example_file.pyx -x -e')
    cyther.core('example_file.pyx -t -e')
    subprocess.call(['cytherize', 'example_file.pyx', '-l', '-cython', '_a', '_l', '-e'])
    cyther.core('example_file.pyx -t -c -e')
    cyther.core('example_file.pyx -t -l -e')
    cyther.core('example_file.pyx -x -l -p minimal -gcc _O4 -e')
    cyther.core('example_file.pyx -x -e')
    cyther.core('example_file.pyx -e')

    cyther.core('-h')

    print('<test_cyther.py> All tests have been passed')

if __name__ == '__main__':
    raise Exception("This file is not to be run directly! See '$cyther test'")
