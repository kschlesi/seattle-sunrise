from __future__ import absolute_import

import pkg_resources
__version__ = pkg_resources.require("seattle_sunrise")[0].version.split('-')[0]

from .light_control import *
