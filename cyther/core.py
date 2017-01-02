
"""
The heart of Cyther
"""

from .system import INFO
from .project import purge_project, clean_project

"""
Each function must have the parameter 'args', even if they do not use it.
This is because they can be called by the parser, and parser always passes a
'args' variable in.
"""


def info(**kwargs):
    print(INFO)


def configure(**kwargs):
    pass


def setup(**kwargs):
    print(kwargs)


def make(**kwargs):
    pass


def build(**kwargs):
    pass


def clean(**kwargs):
    clean_project()


def purge(**kwargs):
    purge_project()
