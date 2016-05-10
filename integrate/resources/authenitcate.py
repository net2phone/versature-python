# -*- coding: utf-8 -*-
from integrate.request_handler import ResourceRequest

__author__ = 'DavidWard'

RESOURCE_PATH = 'oauth/'
TOKEN_RESOURCE_PATH = 'oauth/token/'


def login(username, password, client_id, vendor_id=None, **kwargs):
    resource_request = ResourceRequest(**kwargs)

    data = {'grant_type': 'password',
            'username': username,
            'password': password,
            'client_id': client_id}

    if vendor_id:
        data['vendor_id'] = vendor_id

    return resource_request.request('POST', path=TOKEN_RESOURCE_PATH, data=data)


def refresh_token(refresh_token, client_id, vendor_id=None, **kwargs):
    resource_request = ResourceRequest(**kwargs)

    data = {'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id}

    if vendor_id:
        data['vendor_id'] = vendor_id

    return resource_request.request('POST', path=TOKEN_RESOURCE_PATH, data=data)