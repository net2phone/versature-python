# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from functools import wraps

from versature.settings import CLIENT_ID, CLIENT_SECRET, VENDOR_ID
from versature.request_handler import ResourceRequest, AuthenticatedResourceRequest
from versature.exceptions import AuthenticationException

__author__ = 'DavidWard'


def obtain_access(func):
    """
    If the is not found or if an access_token has expired and a refresh token is found then attempt to update the token
    :param func:
    :return:
    """
    @wraps(func)
    def retry_if_token_expired(self, *args, **kwargs):
        try:
            if self.user.access_token is None:
                self.authenticate()

            return func(self, *args, **kwargs)
        except AuthenticationException as e:
            if self.refresh_token:
                result = self.refresh_token_grant(self.refresh_token)
                self.user.access_token = result['access_token']
                return func(self, *args, **kwargs)
            else:
                raise e
    return retry_if_token_expired


class User(object):

    def __init__(self, username=None, password=None, access_token=None, refresh_token=None,
                 expires=None, expires_in=None, scope=None, token_change_func=None, request_handler=None):
        self.token_change_func = token_change_func
        self.username = username
        self.password = password
        self._access_token = access_token
        self.refresh_token = refresh_token
        self.scope = scope
        self.expires = expires
        if expires_in:
            self.expires_in = datetime.utcnow() + timedelta(seconds=expires_in)

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value
        if self.token_change_func:
            self.token_change_func(self.username, self.access_token, self.refresh_token, self.expires, self.scope)

    @access_token.deleter
    def access_token(self):
        del self._access_token

    def __setattr__(self, name, value):
        if name == 'expires_in':
            self.expires = datetime.utcnow() + timedelta(seconds=value) if value else None
        super(User, self).__setattr__(name, value)

    def update_from_authentication_result(self, result):
        self.access_token = result.get('access_token', None)
        self.refresh_token = result.get('refresh_token', None)
        self.expires_in = result.get('expires_in', None)
        self.scope = result.get('scope', None)


class Versature(object):

    def __init__(self, user=None, username=None, password=None, access_token=None, refresh_token=None,
                 expires=None, expires_in=None, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, vendor_id=VENDOR_ID,
                 token_change_func=None, request_handler=None):
        self.user = user

        if user is None:
            self.user = User(username=username, password=password, access_token=access_token,
                             refresh_token=refresh_token, expires=expires, expires_in=expires_in,
                             token_change_func=token_change_func)

        self.client_id = client_id
        self.client_secret = client_secret
        self.vendor_id = vendor_id
        self.request_handler = request_handler

    def authenticate(self):
        """
        Authenticate the current user
        :return:
        """
        # If already  have token then return
        if self.user.access_token:
            return

        if self.user.username and self.user.password:
            result = self.password_grant(self.user.username, self.user.password)
            self.user.update_from_authentication_result(result)
        elif self.client_id and self.client_secret:
            result = self.client_credentials_grant()
            self.user.update_from_authentication_result(result)

    def client_credentials_grant(self, **kwargs):
        """
        Get an Access Token with the provided confidential client id and secret. No refresh token will be available
        for this grant type.
        :param kwargs:
        :return:
        """
        resource_request = ResourceRequest(request_handler=self.request_handler, **kwargs)

        data = {'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret}

        if self.vendor_id:
            data['vendor_id'] = self.vendor_id

        return resource_request.request('POST', path='oauth/token/', data=data)

    def password_grant(self, username, password, **kwargs):
        """
        Get an access token and possible refresh token given the username and password provided.
        NOTE. A valid client_id must be provided to authenticate this application.
        :param username:
        :param password:
        :param kwargs:
        :return:
        """
        resource_request = ResourceRequest(request_handler=self.request_handler, **kwargs)

        data = {'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id': self.client_id}

        if self.vendor_id:
            data['vendor_id'] = self.vendor_id

        return resource_request.request('POST', path='oauth/token/', data=data)

    def refresh_token_grant(self, refresh_token, **kwargs):
        """
        Refresh the provided token. If this operation is permitted for the

        :param refresh_token:
        :param kwargs:
        :return:
        """
        resource_request = ResourceRequest(**kwargs)

        data = {'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id}

        if self.vendor_id:
            data['vendor_id'] = self.vendor_id

        return resource_request.request('POST', path='oauth/token/', data=data)

    @obtain_access
    def read_active_calls(self, all=False, **kwargs):
        """
        Get a list of calls which are currently active/ongoin
        :param all:
        :param kwargs:
        :return:
        """
        authenticated_resource_request = AuthenticatedResourceRequest(access_token=self.user.access_token, request_handler=self.request_handler, **kwargs)
        params = {'all': all}
        return authenticated_resource_request.request('GET', params=params, path='calls/')

    @obtain_access
    def place_call(self, fr, to, auto_answer=False, **kwargs):
        """
        Place a call from a given user to a given destination. If support auto_answer will pick up/connect the call
        automatically.
        :param fr:
        :param to:
        :param auto_answer:
        :param kwargs:
        :return:
        """
        authenticated_resource_request = AuthenticatedResourceRequest(access_token=self.user.access_token, request_handler=self.request_handler, **kwargs)

        params = {'to': to,
                  'from': fr,
                  'auto_answer': auto_answer}

        return authenticated_resource_request.request('POST', params=params, path='calls/')

    @obtain_access
    def answer_call(self, id, to, **kwargs):
        """
        Answer a call with the provided id
        :param id:
        :param to:
        :param kwargs:
        :return:
        """
        authenticated_resource_request = AuthenticatedResourceRequest(access_token=self.user.access_token, request_handler=self.request_handler, **kwargs)

        data = {'id': id,
                'to': to}
        path = 'calls/{id}/answer/'.format(id=id)

        return authenticated_resource_request.request('PUT', data=data, path=path)

    @obtain_access
    def terminate_call(self, id, **kwargs):
        """
        Hang Up/End a call with the provided id
        :param id:
        :param kwargs:
        :return:
        """
        authenticated_resource_request = AuthenticatedResourceRequest(access_token=self.user.access_token, request_handler=self.request_handler, **kwargs)
        path = 'calls/{id}'.format(id=id)

        return authenticated_resource_request.request('DELETE', path=path)

    # Types of CDRs which are identifiable
    CDR_TYPE_INBOUND = 'Inbound'
    CDR_TYPE_OUTBOUND = 'Outbound'
    CDR_TYPE_MISSED = 'Missed'
    CDR_TYPES = [CDR_TYPE_INBOUND, CDR_TYPE_OUTBOUND, CDR_TYPE_MISSED]

    @obtain_access
    def get_cdrs(self, start_date=None, end_date=None, type=None, all=False, **kwargs):
        """
        Get the call records for a given time period for the users specified. If provided the id will
        be used to get the call records for that user. If not specified call records will be fetched for the currently
        authenticated user. If you wish to retrieve all calls across your domain use the "all" argument.

        :param start_date:
        :param end_date:
        :param type:
        :param all:
        :return:
        """
        authenticated_resource_request = AuthenticatedResourceRequest(access_token=self.user.access_token, request_handler=self.request_handler, **kwargs)
        params = {'start_date': start_date,
                  'end_date': end_date,
                  'type': type,
                  'all': all}

        #TODO Create exception if argument doesn't match expected values.
        if type is not None:
            assert (type in self.CDR_TYPES)

        return authenticated_resource_request.request('GET', path='cdrs/', params=params)

    @obtain_access
    def get_call_queue_stats(self, **kwargs):
        """
        Get the call queue stats
        :return:
        """
        authenticated_resource_request = AuthenticatedResourceRequest(access_token=self.user.access_token, request_handler=self.request_handler, **kwargs)
        return authenticated_resource_request.request('GET', path='call_queues/stats/')
