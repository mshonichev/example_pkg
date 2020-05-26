#!/usr/bin/env python3

from .result import Result, ResultLinesCollector
from .sshpool import SshPool
from .tidenexception import TidenException
from .util import *
from .assertions import *

import pluggy
hookimpl = pluggy.HookimplMarker("tiden")
"""Marker to be imported and used in Tiden hooks implementations"""


