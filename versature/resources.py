# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
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

            if self.user.refresh_token:

                try:

                    result = self.refresh_token_grant(self.user.refresh_token)
                    self.user.expires = result['expires']
                    self.user.access_token = result['access_token']
                    return func(self, *args, **kwargs)

                except AuthenticationException:

                    # If we know the username and password then get a new set of tokens
                    if self.user.username and self.user.password:
                        result = self.password_grant(self.user.username, self.user.password)
                        self.user.update_from_authentication_result(result)
                        return func(self, *args, **kwargs)
                    else:
                        raise

            elif self.client_id and self.client_secret:

                result = self.client_credentials_grant()
                self.user.access_token = result['access_token']
                return func(self, *args, **kwargs)

            else:
                raise

    return retry_if_token_expired


class User(object):

    def __init__(self, username=None, password=None, access_token=None, refresh_token=None,
                 expires=None, expires_in=None, scope=None):
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
        self.token_change()

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

    def token_change(self):
        """
        Function called when the access token is updated. Override for custom functionality when the token chagnes
        :return:
        """
        pass


class CursorResponse(object):
    """
    A cursor response object contains details about additional data which is available for this request.
    """

    def __init__(self, data, headers):
        self.data = data
        self.more = headers.get('more', False)
        self.cursor = headers.get('cursor', False)


class Versature(object):

    def __init__(self, user=None, username=None, password=None, access_token=None, refresh_token=None,
                 expires=None, expires_in=None, api_url=API_URL, api_version=API_VERSION, client_id=CLIENT_ID,
                 client_secret=CLIENT_SECRET, vendor_id=VENDOR_ID, request_handler=None, storage=None):
        self.user = user

        if user is None:
            self.user = User(username=username, password=password, access_token=access_token,
                             refresh_token=refresh_token, expires=expires, expires_in=expires_in)

        self.api_url = api_url
        self.api_version = api_version
        self.client_id = client_id
        self.client_secret = client_secret
        self.vendor_id = vendor_id
        self.request_handler = request_handler
        self.storage = storage

    ########################
    #### Helper Methods ####
    ########################

    def resource_request(self, api_version=None, use_storage=False, **kwargs):
        """
        Make a request for a resource
        :return:
        """
        api_version = api_version or self.api_version

        return ResourceRequest(api_url=self.api_url, api_version=api_version, request_handler=self.request_handler,
                               storage=self.storage if use_storage else None,
                               **kwargs)

    def authenticated_resource_request(self, api_version=None, use_storage=False, **kwargs):
        """
        Make a request for an authenticated resource
        :return:
        """
        api_version = api_version or self.api_version
        return AuthenticatedResourceRequest(api_url=self.api_url,
                                            api_version=api_version,
                                            access_token=self.user.access_token,
                                            request_handler=self.request_handler,
                                            storage=self.storage if use_storage else None,
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

        return self.resource_request(use_storage=False).request('POST', path='oauth/token/', data=data)

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

        return self.resource_request(use_storage=False).request('POST', path='oauth/token/', data=data)

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

        return self.resource_request(use_storage=False).request('POST', path='oauth/token/', data=data)

    ###############
    #### Calls ####
    ###############

    @obtain_access
    def active_calls(self, user=None, **kwargs):
        """
        Get a list of calls which are currently active/ongoing
        
        Documentation: http://integrate.versature.com/apidoc/#api-CallsGroup-List_Active_Calls
        
        :param user: The user to get active calls for
        :param kwargs:
        :return:
        """

        if user:
            path = 'calls/users/{user}/active/'.format(user=user)
        else:
            path = 'calls/active/'

        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

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
    def answer_call(self, call_id, to, **kwargs):
        """
        Answer a call with the provided call_id
        :param call_id:
        :param to:
        :param kwargs:
        :return:
        """

        path = 'calls/{call_id}/answer/'.format(call_id=call_id)

        data = {'to': to}

        return self.authenticated_resource_request(**kwargs).request('PUT', data=data, path=path)

    @obtain_access
    def terminate_call(self, call_id, **kwargs):
        """
        Hang Up/End a call with the provided id

        :param call_id:
        :param kwargs:
        :return:
        """
        path = 'calls/{call_id}/'.format(call_id=call_id)
        return self.authenticated_resource_request(**kwargs).request('DELETE', path=path)

    ##############
    #### CDRs ####
    ##############

    @obtain_access
    def cdrs(self, start_date=None, end_date=None, user=None, offset=0, limit=100, **kwargs):
        """
        Get the call records for a given time period for the users specified. If provided the id will
        be used to get the call records for that user. If not specified call records will be fetched for the currently
        authenticated user. If you wish to retrieve all calls across your domain use the "all" argument.

        Documentation: http://integrate.versature.com/apidoc/#api-CDRsGroup-Get_Call_Detail_Records__CDR_s__for_one_or_more_users_

        :param start_date:
        :param end_date:
        :param user: The user whos calls should be collected. i.e. 101
        :param offset: Offset the result by this amount.
        :param limit: Max 200, the number of results to be returned
        :return:
        """

        if user:
            path = 'cdrs/users/{user}/'.format(user=user)
        else:
            path = 'cdrs/'

        params = {'start_date': start_date,
                  'end_date': end_date,
                  'offset': offset,
                  'limit': limit}

        return self.authenticated_resource_request(**kwargs).request('GET', path=path, params=params)

    #####################
    #### Call Queues ####
    #####################

    @obtain_access
    def call_queues(self, queue=None, **kwargs):
        """
        Get a list of call queues in a domain. If provided the queue will be used to get the details for a specific Call Queue.

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueues-Call_Queues
        :param queue:
        :param kwargs:
        :return:
        """
        if queue:
            path = 'call_queues/{queue}/'.format(queue=queue)
        else:
            path = 'call_queues/'

        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

    @obtain_access
    def call_queue_stats(self, queue=None, start_date=None, end_date=None, **kwargs):
        """
        Get the stats for one or more call queues.

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesStats-Call_Queue_Stats

        :param queue: The user id of the queue you wish to receive stats for.
        :param start_date:
        :param end_date:
        :return:
        """

        if queue:
            path = 'call_queues/{queue}/stats/'.format(queue=queue)
        else:
            path = 'call_queues/stats/'

        params = {'start_date': start_date,
                  'end_date': end_date}

        return self.authenticated_resource_request(**kwargs).request('GET', path=path, params=params)

    @obtain_access
    def call_queue_live_stats(self, queue=None, **kwargs):
        """
        Get the current live stats for one or more call queues.

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesStats-Live_Call_Queue_Stats

        :param queue: The user id of the queue you wish to receive stats for.
        :return:
        """

        if queue:
            path = 'call_queues/{queue}/stats/live/'.format(queue=queue)
        else:
            path = 'call_queues/stats/live/'

        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

    @obtain_access
    def call_queue_agent_stats(self, queue=None, start_date=None, end_date=None, inbound=True, outbound=True, **kwargs):
        """
        Get the stats for agents for one or more call queues.

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesStats-Call_Queue_Agent_Stats

        :param queue: The user id of the agent you wish to receive stats for.
        :param start_date:
        :param end_date:
        :return:
        """
        if queue:
            path = 'call_queues/{queue}/agents/stats/'.format(queue=queue)
        else:
            path = 'call_queues/agents/stats/'

        if not inbound:
            path = path + 'outbound/'

        if not outbound:
            path = path + 'inbound/'

        if not inbound and not outbound:
            path = 'call_queues/{queue}/agents/stats/'.format(queue=queue) if queue else 'call_queues/agents/stats/'

        params = {'start_date': start_date,
                  'end_date': end_date}

        return self.authenticated_resource_request(**kwargs).request('GET', path=path, params=params)

    @obtain_access
    def call_queue_abandoned_call_report(self, queue=None, start_date=None, end_date=None, **kwargs):
        """
        Get a report indicating the volume of calls which were abandoned.

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesReports-Call_Queue_Abandoned_Call_Report

        :param queue: The user id of the queue you wish to receive the report for.
        :param start_date:
        :param end_date:
        :return:
        """

        if queue:
            path = 'call_queues/{queue}/reports/abandoned_calls/'.format(queue=queue)
        else:
            path = 'call_queues/reports/abandoned_calls/'

        params = {'start_date': start_date,
                  'end_date': end_date}

        return self.authenticated_resource_request(**kwargs).request('GET', path=path, params=params)

    # Types of periods which are identifiable
    HOUR = 'hour'
    DAY = 'day'
    MONTH = 'month'
    REPORT_PERIODS = [HOUR, DAY, MONTH]

    @obtain_access
    def call_queue_dialled_numbers_report(self, queue=None, start_date=None, end_date=None, period=None, **kwargs):
        """
        Get a report indicating the number of calls handled by the call queues split into periods/ranges.

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesReports-Call_Queue_Dialled_Number_Report

        :param queue: The user id of the queue you wish to receive the report for.
        :param start_date:
        :param end_date:
        :param period:
        :return:
        """

        if queue:
            path = 'call_queues/{queue}/reports/dialled_numbers/'.format(queue=queue)
        else:
            path = 'call_queues/reports/dialled_numbers/'

        if period is not None:
            if period not in self.REPORT_PERIODS:
                raise TypeError('%s is not a valid Period. Expected one of: %s' % (type, self.REPORT_PERIODS))

        params = {'start_date': start_date,
                  'end_date': end_date,
                  'period': period}

        return self.authenticated_resource_request(**kwargs).request('GET', path=path, params=params)

    @obtain_access
    def call_queue_split_report(self, queue=None, start_date=None, end_date=None, period=None, **kwargs):
        """
        Get a report indicating the number of calls handled by the call queues split into periods/ranges.

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesReports-Call_Queue_Split_Report

        :param queue: The user id of the queue you wish to receive the report for.
        :param start_date:
        :param end_date:
        :param period:
        :return:
        """

        if queue:
            path = 'call_queues/{queue}/reports/splits/'.format(queue=queue)
        else:
            path = 'call_queues/reports/splits/'

        if period is not None:
            if period not in self.REPORT_PERIODS:
                raise TypeError('%s is not a valid Period. Expected one of: %s' % (type, self.REPORT_PERIODS))

        params = {'start_date': start_date,
                  'end_date': end_date,
                  'period': period}

        return self.authenticated_resource_request(**kwargs).request('GET', path=path, params=params)

    @obtain_access
    def call_queue_terminating_agents_report(self, queue=None, start_date=None, end_date=None, period=None, **kwargs):
        """
        Get a report indicating the volume of calls handled by the agents of the call queues.

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesReports-Call_Queue_Terminating_Agent_Report

        :param queue: The user id of the queue you wish to receive the report for.
        :param start_date:
        :param end_date:
        :param period:
        :return:
        """

        if queue:
            path = 'call_queues/{queue}/reports/terminating_agents/'.format(queue=queue)
        else:
            path = 'call_queues/reports/terminating_agents/'

        if period is not None:
            if period not in self.REPORT_PERIODS:
                raise TypeError('%s is not a valid Period. Expected one of: %s' % (type, self.REPORT_PERIODS))

        params = {'start_date': start_date,
                  'end_date': end_date,
                  'period': period}

        return self.authenticated_resource_request(**kwargs).request('GET', path=path, params=params)

    @obtain_access
    def call_queue_agents(self, queue=None, **kwargs):
        """
        Get info about the users

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesAgents-Call_Queue_Agents

        :param queue: The queue you wish to receive information for.
        :return:
        """

        if queue:
            path = 'call_queues/{queue}/agents/'.format(queue=queue)
        else:
            path = 'call_queues/agents/'

        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

    @obtain_access
    def log_agent_in(self, queue, agent, device, **kwargs):
        """
        Log an agent into a queue

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesAgents-Call_Queue_Login

        :param queue: The queue you wish to sign into
        :param agent: The agent who should be signed in
        :param device: The agent's device which will be logged into the queue
        :return:
        """

        path = 'call_queues/{queue}/agents/{agent}/devices/{device}/login/'.format(queue=queue, agent=agent, device=device)
        return self.authenticated_resource_request(**kwargs).request('PUT', path=path)

    @obtain_access
    def log_agent_out(self, queue, agent, device, **kwargs):
        """
        Log an agent out of a queue

        Documentation: http://integrate.versature.com/apidoc/#api-CallQueuesAgents-Call_Queue_Logout

        :param queue: The queue you wish to sign into
        :param agent: The agent who should be signed in
        :param device: The agent's device which will be logged into the queue
        :return:
        """

        path = 'call_queues/{queue}/agents/{agent}/devices/{device}/logout/'.format(queue=queue, agent=agent, device=device)
        return self.authenticated_resource_request(**kwargs).request('PUT', path=path)

    #################
    #### Account ####
    #################

    @obtain_access
    def current_account(self, **kwargs):
        """
        Get info about the current account

        :param user: The user/extension of the caller you wish to receive information for.
        :return:
        """

        path = 'accounts/current/'

        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

    ###############
    #### Users ####
    ###############

    @obtain_access
    def users(self, user=None, **kwargs):
        """
        Get info about the users

        Documentation: http://integrate.versature.com/apidoc/#api-UsersGroup-Users

        :param user: The user/extension of the caller you wish to receive information for.
        :return:
        """

        if user:
            path = 'users/{user}/'.format(user=user)
        else:
            path = 'users/'

        return self.authenticated_resource_request(**kwargs).request('GET', path=path)


    @obtain_access
    def current_user(self, **kwargs):
        """
        Get info about the current user
        Documentation: http://integrate.versature.com/apidoc/#api-UsersGroup-Current_User
        :param user: The user/extension of the caller you wish to receive information for.
        :return:
        """

        path = 'users/current/'

        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

    #######################
    #### Subscriptions ####
    #######################
    @obtain_access
    def create_subscription(self, post_uri, expires_in=7200, calls=False, cdrs=False, cdr_creation=False, recordings=False, recording_analytics=False, raw=False, user='*', **kwargs):
        """
        create a subscription
        :param post_uri: 
        :param expires_in: 
        :param calls: 
        :param cdrs: 
        :param cdr_creation: 
        :param recordings: 
        :param recording_analytics: 
        :param raw: 
        :param user: 
        :param kwargs: 
        :return: 
        """
        path = 'subscriptions/'
        params = {'post_uri': post_uri,
                  'expires_in': expires_in,
                  'calls': calls,
                  'cdrs': cdrs,
                  'cdr_creation': cdr_creation,
                  'recordings': recordings,
                  'recording_analytics': recording_analytics,
                  'raw': raw,
                  'user': user}

        return self.authenticated_resource_request(**kwargs).request('POST', path=path, params=params)

    @obtain_access
    def read_subscription(self, subscription_id, **kwargs):
        """
        get info about subscription
        :param subscription_id: 
        :param kwargs: 
        :return: 
        """
        path = 'subscriptions/{subscriptions_id}'.format(subscriptions_id=subscription_id)
        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

    @obtain_access
    def delete_subscription(self, subscription_id, **kwargs):
        """
        delete subscription
        :param subscription_id: 
        :param kwargs: 
        :return: 
        """
        path = 'subscriptions/{subscriptions_id}'.format(subscriptions_id=subscription_id)
        return self.authenticated_resource_request(**kwargs).request('DELETE', path=path)

    #################
    #### Devices ####
    #################

    @obtain_access
    def devices(self, user=None, **kwargs):
        """
        Get devices for one or more users

        Documentation: http://integrate.versature.com/apidoc/#api-DeviceGroup-Domain_Devices

        :param user: The user/extension of the caller you wish to receive device information for.
        :return:
        """

        if user:
            path = 'devices/users/{user}/'.format(user=user)
        else:
            path = 'devices/users/'

        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

    @obtain_access
    def current_user_devices(self, **kwargs):
        """
        Get devices for the authenticated user

        Documentation: http://integrate.versature.com/apidoc/#api-DeviceGroup-Current_User_Devices

        :return:
        """
        return self.authenticated_resource_request(**kwargs).request('GET', path='devices/users/current/')


    ####################
    #### Recordings ####
    ####################

    @obtain_access
    def recordings(self, call_id, **kwargs):
        """
        Get the call recording with the provided call id

        Documentation: http://integrate.versature.com/apidoc/#api-RecordingsGroup-Get_Recordings_for_a_given_call

        :param call_id: The call id for a device with recording enabled
        :return:
        """
        path = 'recordings/call_ids/{call_id}/'.format(call_id=call_id)
        return self.authenticated_resource_request(**kwargs).request('GET', path=path)

    #######################
    #### Phone Numbers ####
    #######################

    @obtain_access
    def phone_numbers(self, **kwargs):
        """
        Get available phone numbers for this domain
    
        :param kwargs: 
        :return: 
        """
        return self.authenticated_resource_request(**kwargs).request('GET', path='phone_numbers/')

    ###########################
    #### Caller Id Numbers ####
    ###########################

    @obtain_access
    def caller_id_numbers(self, **kwargs):
        """
        Get available caller id numbers for this domain
    
        :param kwargs: 
        :return: 
        """
        return self.authenticated_resource_request(**kwargs).request('GET', path='caller_id_numbers/')

    @obtain_access
    def add_caller_id_number(self, e164, description, **kwargs):
        """
        Add a caller id for this domain
    
        :param e164: 
        :param description: 
        :param kwargs: 
        :return: 
        """
        params = {'e164': e164,
                  'description': description}

        return self.authenticated_resource_request(**kwargs).request('POST', params=params, path='caller_id_numbers/')

    @obtain_access
    def update_caller_id_number(self, e164, description, **kwargs):
        """
        Update the description for a caller id for this domain
    
        :param e164: 
        :param description: 
        :param kwargs: 
        :return: 
        """
        path = 'caller_id_numbers/{e164}/'.format(e164=e164)
        params = {'description': description}
        return self.authenticated_resource_request(**kwargs).request('PUT', params=params, path=path)

    @obtain_access
    def delete_caller_id_number(self, e164, **kwargs):
        """
        Remove the a caller id for this domain
    
        :param e164: 
        :param kwargs: 
        :return: 
        """
        path = 'caller_id_numbers/{e164}/'.format(e164=e164)
        return self.authenticated_resource_request(**kwargs).request('DELETE', path=path)


#############################
####### UNIT TESTS    #######
#############################

class VersatureUnitTest(Versature):

    ###############
    ## Integrate ##
    ###############
    @obtain_access
    def test_integrate_call_queue_stats(self, scope, version, vendor_id, **kwargs):
        """
        call test case on integrate for call queue stats
        :return: 
        """
        path = 'unit_tests/integrate/call_queues/stats/'
        params = {'scope': scope, 'api_version': version, 'vendor_id': vendor_id}
        return self.authenticated_resource_request(**kwargs).request('GET', params=params, path=path)

    @obtain_access
    def test_integrate_cdrs(self, scope, version, vendor_id, **kwargs):
        """
        call test case on integrate for cdrs
        :return: 
        """
        path = 'unit_tests/integrate/cdrs/'
        params = {'scope': scope, 'api_version': version, 'vendor_id': vendor_id}
        return self.authenticated_resource_request(**kwargs).request('GET', params=params, path=path)

    @obtain_access
    def test_integrate_devices(self, scope, version, vendor_id, **kwargs):
        """
        call test case on integrate for devices
        :return: 
        """
        path = 'unit_tests/integrate/devices/'
        params = {'scope': scope, 'api_version': version, 'vendor_id': vendor_id}
        return self.authenticated_resource_request(**kwargs).request('GET', params=params, path=path)

    @obtain_access
    def test_integrate_subscriptions_calls(self, scope, version, vendor_id, **kwargs):
        """
        call test case for call subscriptions
        :param scope: 
        :param version: 
        :param vendor_id: 
        :param kwargs: 
        :return: 
        """
        path = 'unit_tests/integrate/subscriptions/calls/'
        params = {'scope': scope, 'api_version': version, 'vendor_id': vendor_id}
        return self.authenticated_resource_request(**kwargs).request('GET', params=params, path=path)


    ################
    ## Netsapiens ##
    ################
    @obtain_access
    def test_netsapiens_call_queue_stats(self, scope, url, **kwargs):
        """
        call test case on integrate for call queue stats
        :return: 
        """
        path = 'unit_tests/netsapiens/call_queues/stats/'
        params = {'scope': scope, 'netsapiens_url': url}
        return self.authenticated_resource_request(**kwargs).request('GET', params=params, path=path)

    @obtain_access
    def test_netsapiens_cdrs(self, scope, url, **kwargs):
        """
        call test case on integrate for cdrs
        :return: 
        """
        path = 'unit_tests/netsapiens/cdrs/'
        params = {'scope': scope, 'netsapiens_url': url}
        return self.authenticated_resource_request(**kwargs).request('GET', params=params, path=path)

    @obtain_access
    def test_netsapiens_devices(self, scope, url, **kwargs):
        """
        call test case on integrate for devices
        :return: 
        """
        path = 'unit_tests/netsapiens/devices/'
        params = {'scope': scope, 'netsapiens_url': url}
        return self.authenticated_resource_request(**kwargs).request('GET', params=params, path=path)