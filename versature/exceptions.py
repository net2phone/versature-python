# -*- coding: utf-8 -*-
__author__ = 'DavidWard'


class VersatureAPIException(Exception):
    pass


class HTTPError(VersatureAPIException):

    def __init__(self, msg, status_code=None):
        super(HTTPError, self).__init__()
        self.msg = msg
        self.status_code = status_code

    def __str__(self):
        if self.status_code:
            return 'Status Code: %s, %s' % (self.status_code, self.msg)
        else:
            return self.msg


class NotFound(HTTPError):
    """
    The requested resource was not found
    """
    def __init__(self, msg='The requested resource was not found.'):
        super(NotFound, self).__init__(msg, 403)


class RateLimitExceeded(HTTPError):
    """
    The request limit for the endpoint has been exceeded.
    """
    def __init__(self, msg='Rate limit exceeded for this endpoint'):
        super(RateLimitExceeded, self).__init__(msg, 429)


class ForbiddenException(HTTPError):
    """

    """
    def __init__(self, msg='The request failed because the user does not have access to this resource.'):
        super(ForbiddenException, self).__init__(msg, 403)


class AuthenticationException(HTTPError):
    """
    """
    def __init__(self, msg='The request failed because the user is not authenticated.'):
        super(AuthenticationException, self).__init__(msg, 401)


class UnprocessableEntityError(HTTPError):
    """
    The request was understood, but contained an inappropriate value.
    """
    def __init__(self, msg='The request was understood, but contained an inappropriate value.'):
        super(UnprocessableEntityError, self).__init__(msg, 422)


class InternalError(HTTPError):
    """
    An Internal Error occurred while processing your request.
    """
    def __init__(self, msg='An Internal Error occurred while processing your request.'):
        super(InternalError, self).__init__(msg, 500)


class AsyncLookupRequired(VersatureAPIException):

    def __init__(self, source, action):
        super(AsyncLookupRequired, self).__init__(source, action)
        self.source = source
        self.action = action


class ContentTypeNotSupported(VersatureAPIException):
    """
    The content type found is not recognized or supported.
    """
    def __init__(self, msg='The content type found is not recognized or supported'):
        super(ContentTypeNotSupported, self).__init__(msg, 500)
