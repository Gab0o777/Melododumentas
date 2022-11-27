class InvalidParamsFormatException(BaseException):
    # Exception raised when function parameters are invalid.

    def __init__(self, message="Params are invalid or in wrong format"):
        super(InvalidParamsFormatException, self).__init__(message)
