class InvalidArgumentNumberException(Exception):
    # Exception raised when argument number is invalid

    def __init__(self, message="Invalid argument number"):
        super(InvalidArgumentNumberException, self).__init__(message)
