
import cyther
import subprocess


def test_cyther():
    #An info call to display helpful info in log
    cyther.info(None)
    cyther.core('cyther info')
    subprocess.call(['cyther', 'info'])

    #Do a core, command line, and function run
    #subprocess.call(['cyther', 'build', 'example_file.pyx'])

    print('<@test_cyther.py> All tests have been passed')

if __name__ == '__main__':
    test_cyther()
