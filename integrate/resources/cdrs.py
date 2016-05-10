# -*- coding: utf-8 -*-

from integrate.request_handler import AuthenticatedResourceRequest

__author__ = 'David Ward'

RESOURCE_PATH = 'cdrs/'

INBOUND = 'Inbound'
OUTBOUND = 'Outbound'
MISSED = 'Missed'

TYPES = [INBOUND, OUTBOUND, MISSED]


def get_cdrs(start_date=None, end_date=None, type=None, all=False, **kwargs):
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

    authenticated_resource_request = AuthenticatedResourceRequest(**kwargs)
    params = {'start_date': start_date,
              'end_date': end_date,
              'type': type,
              'all': all}

    #TODO Create exception if argument doesn't match expected values.
    if type is not None:
        assert (type in TYPES)

    return authenticated_resource_request.request('GET', path=RESOURCE_PATH, params=params)

