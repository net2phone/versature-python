# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import parser
from functools import wraps

from .settings import CLIENT_ID, CLIENT_SECRET, VENDOR_ID, API_URL, API_VERSION
from .request_handler import ResourceRequest, AuthenticatedResourceRequest
from .exceptions import AuthenticationException

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
            if self.user.refresh_token and self.user.token_change_func:
                result = self.refresh_token_grant(self.user.refresh_token)
                self.user.expires = parser.parse(result['expires'])
                self.user.access_token = result['access_token']
                return func(self, *args, **kwargs)
            else:
                raise e
    return retry_if_token_expired


class User(object):

    def __init__(self, username=None, password=None, access_token=None, refresh_token=None,
                 expires=None, expires_in=None, scope=None, token_change_func=None):
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
            self.token_change_func(self.access_token, self.refresh_token, self.expires)

    @access_token.deleter
    def access_token(self):
        del self._access_token

    def __setattr__(self, name, value):
        if name == 'expires_in':
            self.expires = datetime.utcnow() + timedelta(seconds=value) if value else None
        super(User, self).__setattr__(name, value)

    def update_from_authentication_result(self, result):
        self.refresh_token = result.get('refresh_token', None)
        self.expires_in = result.get('expires_in', None)
        self.scope = result.get('scope', None)
        self.access_token = result.get('access_token', None)


class Versature(object):

    def __init__(self, user=None, username=None, password=None, access_token=None, refresh_token=None,
                 expires=None, expires_in=None, api_url=API_URL, api_version=API_VERSION, client_id=CLIENT_ID,
                 client_secret=CLIENT_SECRET, vendor_id=VENDOR_ID, token_change_func=None, request_handler=None):
        self.user = user

        if user is None:
            self.user = User(username=username, password=password, access_token=access_token,
                             refresh_token=refresh_token, expires=expires, expires_in=expires_in,
                             token_change_func=token_change_func)

        self.api_url = api_url
        self.api_version = api_version
        self.client_id = client_id
        self.client_secret = client_secret
        self.vendor_id = vendor_id
        self.request_handler = request_handler

    ########################
    #### Helper Methods ####
    ########################

    def resource_request(self, api_version=None, **kwargs):
        """
        Make a request for a resource
        :return:
        """
        api_version = api_version or self.api_version
        return ResourceRequest(api_url=self.api_url, api_version=api_version, request_handler=self.request_handler, **kwargs)

    def authenticated_resource_request(self, api_version=None, **kwargs):
        """
        Make a request for an authenticated resource
        :return:
        """
        api_version = api_version or self.api_version
        return AuthenticatedResourceRequest(api_url=self.api_url,
                                            api_version=api_version,
                                            access_token=self.user.access_token,
                                            request_handler=self.request_handler,
                                            **kwargs)

    #######################
    #### Authorization ####
    #######################

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

    def client_credentials_grant(self):
        """
        Get an Access Token with the provided confidential client id and secret. No refresh token will be available
        for this grant type.
        :param kwargs:
        :return:
        """
        data = {'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret}

        if self.vendor_id:
            data['vendor_id'] = self.vendor_id

        return self.resource_request().request('POST', path='oauth/token/', data=data)

    def password_grant(self, username, password):
        """
        Get an access token and possible refresh token given the username and password provided.
        NOTE. A valid client_id must be provided to authenticate this application.
        :param username:
        :param password:
        :param kwargs:
        :return:
        """
        data = {'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id': self.client_id}

        if self.vendor_id:
            data['vendor_id'] = self.vendor_id

        return self.resource_request().request('POST', path='oauth/token/', data=data)

    def refresh_token_grant(self, refresh_token):
        """
        Refresh the provided token. If this operation is permitted for the

        :param refresh_token:
        :param kwargs:
        :return:
        """
        data = {'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id}

        if self.vendor_id:
            data['vendor_id'] = self.vendor_id

        return self.resource_request().request('POST', path='oauth/token/', data=data)

    ###############
    #### Calls ####
    ###############

    @obtain_access
    def active_calls(self, all=False, **kwargs):
        """
        Get a list of calls which are currently active/ongoing
        :param all:
        :param kwargs:
        :return:
        """
        params = {'all': all}
        return self.authenticated_resource_request(**kwargs).request('GET', params=params, path='calls/')

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
        params = {'to': to,
                  'from': fr,
                  'auto_answer': auto_answer}

        return self.authenticated_resource_request(**kwargs).request('POST', params=params, path='calls/')

    @obtain_access
    def answer_call(self, id, to, **kwargs):
        """
        Answer a call with the provided id
        :param id:
        :param to:
        :param kwargs:
        :return:
        """
        data = {'id': id,
                'to': to}
        path = 'calls/{id}/answer/'.format(id=id)

        return self.authenticated_resource_request(**kwargs).request('PUT', data=data, path=path)

    @obtain_access
    def terminate_call(self, id, **kwargs):
        """
        Hang Up/End a call with the provided id

        :param id:
        :param kwargs:
        :return:
        """
        path = 'calls/{id}'.format(id=id)
        return self.authenticated_resource_request(**kwargs).request('DELETE', path=path)


    ##############
    #### CDRs ####
    ##############

    # Types of CDRs which are identifiable
    CDR_TYPE_INBOUND = 'Inbound'
    CDR_TYPE_OUTBOUND = 'Outbound'
    CDR_TYPE_MISSED = 'Missed'
    CDR_TYPES = [CDR_TYPE_INBOUND, CDR_TYPE_OUTBOUND, CDR_TYPE_MISSED]

    @obtain_access
    def cdrs(self, start_date=None, end_date=None, type=None, all=False, offset=0, limit=100, **kwargs):
        """
        Get the call records for a given time period for the users specified. If provided the id will
        be used to get the call records for that user. If not specified call records will be fetched for the currently
        authenticated user. If you wish to retrieve all calls across your domain use the "all" argument.

        Documentation: http://integrate.versature.com/apidoc/#api-CDRsGroup-Get_Call_Detail_Records__CDR_s__for_one_or_more_users

        :param start_date:
        :param end_date:
        :param type:
        :param all:
        :param offset: Offset the result by this amount.
        :param limit: Max 200, the number of results to be returned
        :return:
        """
        params = {'start_date': start_date,
                  'end_date': end_date,
                  'type': type,
                  'all': all,
                  'offset': offset,
                  'limit': limit}

        if type is not None:
            if type not in self.CDR_TYPES:
                raise TypeError('%s is not a valid CDR Type. Expected one of: %s' % (type, self.CDR_TYPES))

        return self.authenticated_resource_request(**kwargs).request('GET', path='cdrs/', params=params)


    #####################
    #### Call Queues ####
    #####################

    @obtain_access
    def call_queue_stats(self, id=None, **kwargs):
        """
        Get the current stats for one or more call queues.

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesGroup-Get_call_queue_stats

        :param id: The user id of the queue you wish to receive stats for.
        :return:
        """
        path = 'call_queues/stats/'
        if id:
            path = '{path}{id}'.format(path=path, id=id)

        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

    ####################
    #### Caller Id ####
    ####################

    @obtain_access
    def caller_ids(self, id, **kwargs):
        """
        Get the Social Caller Id details for the provided id.

        Documentation: http://integrate.versature.com/apidoc/#api-CallerIdGroup-Get_Caller_Id__Closed_Beta_

        :param id: The user id of the caller you wish to receive information for.
        :return:
        """
        path = 'caller_ids/{id}/'.format(id=id)
        return self.authenticated_resource_request(**kwargs).request('GET', path=path)


    ####################
    #### Users ####
    ####################

    @obtain_access
    def users(self, id=None, **kwargs):
        """
        Get info about the user with the given id

        :param id: The user/extension of the caller you wish to receive information for.
        :return:
        """
        path = 'users/'
        if id:
            path = '{path}{id}/'.format(path=path, id=id)
        return self.authenticated_resource_request(**kwargs).request('GET', path=path)
