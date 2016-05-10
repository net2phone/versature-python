# -*- coding: utf-8 -*-
__author__ = 'DavidWard'


class VersatureAPIException(Exception):
    pass


class HTTPError(VersatureAPIException):

    def __init__(self, msg, response=None, status_code=None):
        super(HTTPError, self).__init__(msg)
        self.response = response
        self.status_code = status_code


class NotFound(HTTPError):
    """
    The requested resource was not found
    """
    def __init__(self, msg):
        super(NotFound, self).__init__(msg or 'The requested resource was not found.', 403)


class RateLimitExceeded(HTTPError):
    """
    The request limit for the endpoint has been exceeded.
    """
    def __init__(self, msg):
        super(RateLimitExceeded, self).__init__(msg or 'Rate limit exceeded for this endpoint', 429)


class AuthenticationException(HTTPError):
    """

    """
    def __init__(self, msg):
        super(AuthenticationException, self).__init__(msg or 'Invalid Credentials Provided', 403)


class UnauthorizedException(HTTPError):
    """
    """
    def __init__(self, msg):
        super(UnauthorizedException, self).__init__(msg or 'The provided token is not valid', 401)


class UnprocessableEntityError(HTTPError):
    """
    The request was understood, but contained an inappropriate value.
    """
    def __init__(self, msg):
        super(UnprocessableEntityError, self).__init__(msg or 'The request was understood, but contained an inappropriate value.', 422)


class InternalError(HTTPError):
    """
    An Internal Error occurred while processing your request.
    """
    def __init__(self, msg):
        super(InternalError, self).__init__(msg or 'An Internal Error occurred while processing your request.', 500)


class AsyncLookupRequired(VersatureAPIException):

    def __init__(self, source, action):
        super(AsyncLookupRequired, self).__init__(source, action)
        self.source = source
        self.action = action
        #self.partial_result = None


class ContentTypeNotSupported(VersatureAPIException):
    pass