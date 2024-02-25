class AppBaseException(Exception):

    def __init__(self, *args: object, message:str|None=None) -> None:
        self.message = message
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"{self.message}"

#TODO: Integrate error logging into the exceptions
"""
Base class for all exceptions raised during an api call
:param message: External message that shown to the api consumer
:param reason: Internal message that log the detailed exception
"""
class ApiException(AppBaseException):
    def __init__(
            self, 
            *args: object, 
            message: str, 
            reason: str) -> None:
        # message is show to the user - goes outside
        self.reason = reason #This registers the internal reason for the exception
        super().__init__(*args, message=message)


class IncompleteParams(ApiException):
    def __init__(self, *args: object, reason: str, message: str) -> None:
        super().__init__(*args, message=message, reason=reason)


class UserAuthError(ApiException):
    def __init__(self, *args: object, reason: str, message = "Email or Password is incorrect") -> None:
        super().__init__(*args, message=message, reason=reason)


class CrudError(ApiException):
    def __init__(self, *args: object, reason: str, message = "Operation Failure") -> None:
        super().__init__(*args, message=message, reason=reason)
