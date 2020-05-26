from tiden import TidenException


class AppException(TidenException):
    pass


class MissedRequirementException(AppException):
    pass