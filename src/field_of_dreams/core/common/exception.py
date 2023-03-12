class ApplicationException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class GatewayError(ApplicationException):
    """Raises on database gateway errors"""


class QueueAccessError(ApplicationException):
    """Rises when the queue is wrong"""


class GameOver(ApplicationException):
    """Raises when the game is over"""


class PlayerLoss(ApplicationException):
    """Raises when the user loses"""


class InvalidCredentials(ApplicationException):
    """Raises when invalid credentials are entered"""
