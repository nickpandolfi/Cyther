# I'm just a small-town (girl) initialization file

from .cyther import core, CytherError, run
from .core import info, configure, test, setup, make, clean, purge


try:
    from shutil import which
except ImportError:
    raise CytherError("The current version of Python doesn't support the"
                      "function 'which', normally located in shutil")


__author__ = "Nicholas C. Pandolfi"

__copyright__ = "Copyright (c) 2016 Nicholas C. Pandolfi"

__credits__ = "Stack Exchange"

__license__ = "MIT"

__email__ = "npandolfi@wpi.edu"

__status__ = "Development"
