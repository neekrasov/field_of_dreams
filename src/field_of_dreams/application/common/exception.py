class ApplicationException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class GatewayError(ApplicationException):
    def __init__(self, message: str) -> None:
        super().__init__(message)