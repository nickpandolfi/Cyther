# Cyther: The Cross-Platform Cython/Python Compiler

We all know the beauties of Cython:

    1) Writing C extensions is as easy as Python
    2) Almost any valid Python is valid Cython, as Cython is a superset of Python
    3) It has the readability of Python, but the speed of C
    4) Minimal effort has to be taken in order to speed up some programs by three to four orders of magnitude
    
However, compiling is not always easy. There are a few places that disutils' 'setup.py' can get tripped up.

    1) vcvarsall.bat not found error
    2) gcc: undefined reference to...
    3) Other errors basically referring to 'compiler not found'
    
Cython may be almost as easy to write as Python, but sometimes nowhere near the level of easiness that it
takes to run Python. This is where Cyther comes into play. Cyther is an attempt at a cross platform compiler
that wields both the standard cython compiler and gcc to make sure that these errors don't happen.
Cyther is extremely easy to use. One can call cyther.py from the command line, or import `core` on the
module level, then call that. Here are a few examples of Cyther's features:

        from cyther import core
        core('cython_file.pyx')
    
    same can be done with:
    
        C:/Python35> cyther cython_file.pyx
        
    Here are some neat little option examples:
    
        from cyther import core
        core('python_file.py -t -l')
        # -t means that cyther will not compile it if the source file is not older than the compiled file
        # -l means that cyther will build locally, if not given, it builds in __cythercache__
    
    Perhaps the most useful feature of Cyther:
    
        from cyther import core
        core('cython_file.pyx -w')
        
    This `-w` command means that cyther will keep looking at that file indefinitely and whenever it sees a change
    in the source code, it will automatically compile it without the user having to do anything. Here is the
    output of the -w option in the command line and stdout:
    
        Compiling the file 'D:\python\notes.py'
        cython -a -p -o D:\python\notes.c D:\python\notes.py -l
        gcc -shared -w -O3 -I D:\Python35\include -L D:\Python35\libs
            -o D:\python\notes.pyd D:\python\notes.c -l python35
        ...<count:1>...
        Compiling the file 'D:\python\test.pyx'
        ...<count:2>...
        Compiling the file 'D:\python\test.pyx'
        ...<count:3>...
        Compiling the file 'D:\python\test2.pyx'
        ...<count:4>...
        
    Keep in mind that anything that you pass to core, you can also pass to cyther from the command line. Now,
    try to meditate on this command:
    
        C:/Python35> cyther cython_file.pyx python_file.py test.pyx -w -l -o something -cython _l
    
    This command will compile these three files, then proceed to watch them continuously, and if they change,
    they will be recompiled. Also, their .c and .a files will be built in the same directory. Even further,
    we pass the option _l (-l) to cython, which will create listing files for the three files specified.
    Notice that we put a -o option, when in reality this makes no sense. Cyther knows this and will erase this
    option before it goes to compile, so the files will not be compiled under the same name. To get an idea
    of what Cyther is currently capable of, type `core('-h')` or `cyther -h` from the command line.

Cyther isn't quite perfect yet, so all the incompatabilities and assumptions that Cyther makes are listed
below. We strongly recommend that you look them over before even touching the download button. In the
near future we hope to make Cyther as polished as possible, and bring the list of assumptions listed below
to a minimum. There are even plans in the works to be able to automatically recompile shared object libraries
that are entirely missing on one's system; critical to Cython compilation.
Assumptions cyther makes about your system:

    1) Your environment path variable is able to be found by `shutil.which`
    2) gcc can work with the option -l pythonXY (libpythonXY.a exists in your libs directory)
    3) Almost any gcc compiled C program will work on Windows
    
Hey you! Yes you. If you notice any bugs or peculiarities, please report them to our bug tracker, it will
help us out a lot:
    <LINK FOR BUG TRACKING>
    
If you have any questions or concerns, or even any suggestions, don't hesitate to contact me at:
    npandolfi@wpi.edu
Happy compiling!!
Tags: Cyther, antibug, vcvarsall.bat, MinGW32, Python, Cython, Python 3.x, compiler, command-line, script
user-friendly, setup.py, gcc
