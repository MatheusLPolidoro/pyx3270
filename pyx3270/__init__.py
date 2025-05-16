# ██████╗ ██╗   ██╗██╗  ██╗██████╗ ██████╗ ███████╗ ██████╗
# ██╔══██╗╚██╗ ██╔╝╚██╗██╔╝╚════██╗╚════██╗╚════██║██╔═████╗
# ██████╔╝ ╚████╔╝  ╚███╔╝  █████╔╝ █████╔╝    ██╔╝██║██╔██║
# ██╔═══╝   ╚██╔╝   ██╔██╗  ╚═══██╗██╔═══╝    ██╔╝ ████╔╝██║
# ██║        ██║   ██╔╝ ██╗██████╔╝███████╗   ██║  ╚██████╔╝
# ╚═╝        ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚══════╝   ╚═╝   ╚═════╝
"""
PYX3270
~~~~~~~~~~~~~~~
Emulador de terminal 3270

"""

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent))

from .emulator import X3270
from .__main__ import replay, record

__author__ = 'MatheusLPolidoro'
__version__ = '0.1.0'
__all__ = ['X3270', 'replay', 'record']
