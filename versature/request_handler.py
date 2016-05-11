# -*- coding: utf-8 -*-

from versature.exceptions import HTTPError, NotFound, ContentTypeNotSupported, RateLimitExceeded, ForbiddenException, \
    UnprocessableEntityError, AuthenticationException
from versature.settings import VERSION, API_URL

__author__ = 'DavidWard'


class ResourceRequest(object):

    def __init__(self, base_url=API_URL, api_version=VERSION, async=False, timeout=60, **kwargs):
        self.base_url = base_url
        self.api_version = api_version
        self._request_handler = None
        self.request_handler = kwargs.pop('request_handler', None) or RequestHandler()
        self.async = async
        self.timeout = timeout
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r', kwargs)

    @property
    def request_handler(self):
        return self._request_handler

    @request_handler.setter
    def request_handler(self, value):
        if not isinstance(value, RequestHandlerBase):
            raise TypeError('Invalid Request Handler Provided. Must be subclass of RequestHandlerBase')
        self._request_handler = value

    def prepare_request(self, headers, params):
        pass

    def resolve_future(self, future, get_content=True):
        response = self.request_handler.resolve_future(future)
        if get_content:
            content = self.parse_result(response)
            return content
        return response

    def parse_result(self, response, callback=None):
        content = self.get_content(response)
        if callback:
            callback(content)
        return content

    def get_content(self, response):
        return self.request_handler.get_content(response)

    def request(self, method, path='', headers=None, params=None, data=None):
        """
        Make a request
        :param method:
        :param url:
        :param headers:
        :param params:
        :param data:
        :param timeout:
        :param async:

        :return:
        """
        if headers is None:
            headers = {}

        self.prepare_request(headers, params)

        if headers:
            filter(None, headers)

        if params:
            filter(None, params)

        if data:
            filter(None, data)

        url = '%s/%s' % (self.base_url, path)
        if self.async:
            # Return a Future Object
            future = self.request_handler.request_async(method, url, params, data, headers, self.timeout)
            return future
        else:
            response = self.request_handler.request(method, url, params, data, headers, self.timeout)
            return self.parse_result(response)


class AuthenticatedResourceRequest(ResourceRequest):

    def __init__(self, access_token, **kwargs):
        self.access_token = access_token
        super(AuthenticatedResourceRequest, self).__init__(**kwargs)

    def prepare_request(self, headers, params):
        headers['Authorization'] = 'Bearer %s' % self.access_token
        headers['Accept'] = "application/vnd.integrate.v%s+json" % self.api_version


class RequestHandlerBase(object):

    @staticmethod
    def get_content(response):
        raise NotImplementedError()

    @staticmethod
    def validate_response(response):
        raise NotImplementedError()

    def request(self, method, url, params=None, data=None, headers=None, timeout=None, **kwargs):
        raise NotImplementedError()

    def request_async(self, method, url, params=None, data=None, headers=None, timeout=None, **kwargs):
        raise NotImplementedError()

    def resolve_future(self, future):
        raise NotImplementedError()


class RequestHandler(RequestHandlerBase):

    def __init__(self):
        from requests_futures.sessions import FuturesSession
        self.session = FuturesSession()

    @staticmethod
    def get_content(response):
        RequestHandler.validate_response(response)
        content_type = response.headers['content-type']

        if 'application/json' in content_type:
            return response.json()
        elif 'text/plain' in content_type:
            return response.text
        else:
            raise ContentTypeNotSupported('Content Type: %s is not supported' % content_type)

    @staticmethod
    def validate_response(response):
        """
        Validate the provided response content and status code.
        :param status_code:
        :return:
        """
        http_error_msg = ''

        if 400 <= response.status_code < 500:
            http_error_msg = '%s Client Error: %s' % (response.status_code, response.reason)

        elif 500 <= response.status_code < 600:
            http_error_msg = '%s Server Error: %s' % (response.status_code, response.reason)

        if response.status_code == 401:
            raise AuthenticationException(http_error_msg)
        elif response.status_code == 403:
            raise ForbiddenException(http_error_msg)
        elif response.status_code == 404:
            raise NotFound(http_error_msg)
        elif response.status_code == 422:
            raise UnprocessableEntityError(http_error_msg)
        elif response.status_code == 429:
            raise RateLimitExceeded(http_error_msg)
        elif http_error_msg:
            raise HTTPError(http_error_msg, response, response.status_code)

    def request(self, method, url, params=None, data=None, headers=None, timeout=None, **kwargs):
        return self.resolve_future(self.session.request(method, url, params=params, data=data, headers=headers, timeout=timeout, **kwargs))

    def request_async(self, method, url, params=None, data=None, headers=None, timeout=None, **kwargs):
        """
        Perform an async request. Can pass background_callback to be called with the result if desired

        :param method:
        :param url:
        :param params:
        :param data:
        :param headers:
        :param kwargs:
        :return:
        """
        return self.session.request(method, url, params=params, data=data, headers=headers, timeout=timeout, **kwargs)

    def resolve_future(self, future):
        """
        response = future.result()
        result = self.get_content(response)
        return result
        """
        return future.result()