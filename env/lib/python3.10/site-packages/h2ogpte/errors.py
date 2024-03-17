from typing_extensions import NotRequired, TypedDict


class H2OGPTEError(Exception):
    def __init__(self, error: "ErrorResponse"):
        self.message: str = error.get("error", "")
        self.request_id: str = error.get("request_id", "")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class ErrorResponse(TypedDict):
    error: str
    request_id: NotRequired[str]


class ObjectNotFoundError(H2OGPTEError):
    """
    Raised when a request refers to an object (such as a collection, a document, etc)
    that no longer exists on the server.

    Note that if an object exists but the user doesn't have permissions to access it,
    then an [UnauthorizedError] will be raised instead.
    """


class InvalidArgumentError(H2OGPTEError):
    pass


class UnauthorizedError(H2OGPTEError):
    pass


class InternalServerError(H2OGPTEError):
    pass


class HTTPError(H2OGPTEError):
    def __init__(self, error: "ErrorResponse", code: int):
        super().__init__(error)
        self.status_code = code

    def __str__(self) -> str:
        return f"HTTPError[{self.status_code}]: {self.message}"
