class APIException(Exception):

    def __init__(self, message):
        self.message = message


class BadRequestError(APIException):
    pass


class ParseError(BadRequestError):
    pass


class ValidationError(BadRequestError):
    pass
