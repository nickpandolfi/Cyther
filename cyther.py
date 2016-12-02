"""
This module is meant to be run as a script to get cyther working even when it
wasn't properly installed.

If the user clones cyther, setup.py is not called, and thus scripts aren't
installed correctly.

When installing using pip, this file IS NOT included, and instead the command
line arg: 'cyther' will call the executable 'scripts/cyther-script'
"""

from cyther.arguments import parser
