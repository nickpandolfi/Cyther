
"""
This module is the console entry point when setup.py was used to install cyther
This module is also run with the -m option from the terminal
"""

import sys
from .arguments import parser


def main(args=None):
    """
    Entry point
    """
    if args is None:
        args = sys.argv[1:]
    parser.parse_args(args)


if __name__ == '__main__':
    main()
