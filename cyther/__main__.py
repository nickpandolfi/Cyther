import sys
from .cyther import core
from .arguments import parser


def main(initialArgs=None):
    if initialArgs is None:
        initialArgs = sys.argv[1:]
    args = parser.parse_args(initialArgs)

    core(args)


if __name__ == '__main__':
    main()
