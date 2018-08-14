# -*- coding: utf-8 -*-
import re
import logging

from dateutil import parser

from .exceptions import HTTPError, NotFound, ContentTypeNotSupported, RateLimitExceeded, ScopeException, \
    UnprocessableEntityError, AuthenticationException, BadRequest

try:
    from requests_futures.sessions import FuturesSession
except ImportError:
    pass

__author__ = 'DavidWard'

_logger = logging.getLogger(__name__)
# Add NullHandler to prevent logging warnings on startup
null_handler = logging.NullHandler()
_logger.addHandler(null_handler)


class ResourceRequest(object):

    def __init__(self, api_url, api_version, async=False, timeout=60, request_handler=None, storage=None, cache_timeout=60):
        self.api_url = api_url
        self.api_version = api_version
        self._request_handler = None
        self.request_handler = request_handler or RequestHandler()
        self.async = async
        self.timeout = timeout
        self.result = None
        self.future = None
        self.storage_key = None
        self.storage = storage
        self.cache_timeout = cache_timeout

    @property
    def request_handler(self):
        return self._request_handler

    @request_handler.setter
    def request_handler(self, value):
        if not isinstance(value, RequestHandlerBase):
            raise TypeError('Invalid Request Handler Provided. Must be subclass of RequestHandlerBase')
        self._request_handler = value

    def prepare_request(self, headers, params):
        """
        Prepare the request headers for this request
        :param headers:
        :param params:
        :return:
        """
        headers['Content-Type'] = 'Application/json; charset=utf-8'
        if self.api_version:
            headers['Accept'] = "application/vnd.integrate.v%s+json" % self.api_version

    def resolve(self, get_content=True):
        response = self.request_handler.resolve_future(self.future)
        if get_content:
            return self.parse_result(response)
        return response

    def parse_result(self, response, callback=None):
        """
        Extract the content and headers from the response
        :param response:
        :param callback:
        :return:
        """
        content, _ = self.get_content(response)

        if self.storage:
            self.storage.set(self.storage_key, content, self.cache_timeout)

        if callback:
            callback(content)
        return content

    def get_content(self, response):
        return self.request_handler.get_content(response)

    def request(self, method, path=None, headers=None, params=None, data=None, files=None):
        """
        Make a request
        :param method:
        :param path:
        :param headers:
        :param params:
        :param data:
        :param files:

        :return:
        """
        if headers is None:
            headers = {}

        self.prepare_request(headers, params)

        if headers:
            filter(None, headers)

        if params:
            filter(None, params)

        if data and isinstance(data, dict):
            filter(None, data)

        self.storage_key = None
        if self.storage:
            self.create_storage_key(path, params, data)
            cached_result = self.storage.get(self.storage_key)
            logging.info("Cached Result: {cached_result}".format(cached_result=cached_result))
            if cached_result:
                return cached_result

        url = '%s/%s' % (self.api_url, path) if path else self.api_url
        if self.async:
            # Return a Future Object
            self.future = self.request_handler.request_async(method, url, params, data, files, headers, self.timeout)
            return self
        else:
            response = self.request_handler.request(method, url, params, data, files, headers, self.timeout)
            return self.parse_result(response)

    def create_storage_key(self, path, params, data):
        """
        Create a storage key
        :param path:
        :param params:
        :param data:
        :return:
        """
        self.storage_key = self.storage.create_storage_key(access_token=None, api_version=self.api_version, path=path,
                                                           params=params, data=data)


class AuthenticatedResourceRequest(ResourceRequest):

    def __init__(self, access_token, **kwargs):
        self.access_token = access_token
        super(AuthenticatedResourceRequest, self).__init__(**kwargs)

    def prepare_request(self, headers, params):
        """
        Prepare the request headers for this request
        :param headers:
        :param params:
        :return:
        """
        super(AuthenticatedResourceRequest, self).prepare_request(headers, params)
        headers['Authorization'] = 'Bearer %s' % self.access_token

    def create_storage_key(self, path, params, data):
        """
        Create a storage key
        :param path:
        :param params:
        :param data:
        :return:
        """
        self.storage_key = self.storage.create_storage_key(access_token=self.access_token, api_version=self.api_version,
                                                           path=path, params=params, data=data)


class RequestHandlerBase(object):

    def get_content(self, response):
        raise NotImplementedError()

    def get_status_code(self, response):
        """
        Get the status code from the response object
        :param response:
        :return:
        """
        raise NotImplementedError()

    def validate_response(self, response):
        raise NotImplementedError()

    def request(self, method, url, params=None, data=None, files=None, headers=None, timeout=None, **kwargs):
        raise NotImplementedError()

    def request_async(self, method, url, params=None, data=None, files=None, headers=None, timeout=None, **kwargs):
        raise NotImplementedError()

    def resolve_future(self, future):
        raise NotImplementedError()

    def json_parser(self, value):
        """
        Additional parsing of json response
        :param value:
        :return:
        """
        for k, v in value.items():

            if isinstance(v, basestring) and re.match('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:(?:\+|\-)\d{2}:\d{2})?', v):

                try:
                    value[k] = parser.parse(v)
                except ValueError as value_error:
                    logging.warning('Datetime format found but could not parse. Attribute: %s, Value: %s, error: %s', k, v, value_error)

            # Convert Float values
            elif isinstance(v, basestring) and re.match('\d*\.\d*', v):

                try:
                    value[k] = float(v)
                except ValueError:
                    pass

        return value


class RequestHandler(RequestHandlerBase):

    def __init__(self):
        self.session = FuturesSession()

    def get_content(self, response):
        """
        Extract the content and the response headers

        :param response:
        :return:
        """
        self.validate_response(response)
        content_type = response.headers['content-type']

        if self.get_status_code(response) == 204:
            return None, response.headers
        elif 'application/json' in content_type:
            return response.json(object_hook=self.json_parser), response.headers
        elif 'text/plain' in content_type:
            return response.text, response.headers
        else:
            raise ContentTypeNotSupported('Content Type: %s is not supported' % content_type)

    def get_status_code(self, response):
        """
        Get the status code from the response object
        :param response:
        :return:
        """
        return response.status_code

    def validate_response(self, response):
        """
        Validate the provided response content and status code.
        :param status_code:
        :return:
        """
        reason = getattr(response, 'reason', None)

        if self.get_status_code(response) == 400:
            _logger.warn(reason)
            raise BadRequest()
        elif self.get_status_code(response) == 401:
            _logger.warn(reason)
            raise AuthenticationException()
        elif self.get_status_code(response) == 403:
            _logger.warn(reason)
            raise ScopeException()
        elif self.get_status_code(response) == 404:
            _logger.warn(reason)
            raise NotFound()
        elif self.get_status_code(response) == 422:
            _logger.warn(reason)
            raise UnprocessableEntityError()
        elif self.get_status_code(response) == 429:
            raise RateLimitExceeded()
        elif 400 <= self.get_status_code(response) < 600:
            raise HTTPError(reason, self.get_status_code(response))

    def request(self, method, url, params=None, data=None, files=None, headers=None, timeout=None, **kwargs):
        return self.resolve_future(self.request_async(method, url, params, data, files, headers, timeout, **kwargs))

    def request_async(self, method, url, params=None, data=None, files=None, headers=None, timeout=None, **kwargs):
        """
        Perform an async request. Can pass background_callback to be called with the result if desired

        :param method:
        :param url:
        :param params:
        :param data:
        :param files:
        :param headers:
        :param timeout:
        :param kwargs:
        :return:
        """
        return self.session.request(method, url, params=params, data=data, files=files, headers=headers, timeout=timeout, **kwargs)

    def resolve_future(self, future):
        """
        response = future.result()
        result = self.get_content(response)
        return result
        """
        return future.result()
