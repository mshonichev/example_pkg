#!/usr/bin/env python3


class TidenException(Exception):
    pass


class SkipException(Exception):
    pass


class FeatureNotEnabled(TidenException):
    pass


class RemoteOperationTimeout(TidenException):
    pass
